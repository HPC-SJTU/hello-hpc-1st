import torch
from tqdm import tqdm


def calculate_dequant(quant_param: torch.Tensor, zero_point: torch.Tensor, scale: torch.Tensor):
    '''
    param: quant_param [..., X//group_num, group_num], zero_point [..., X//group_num, 1 ], scale [..., X//group_num, 1 ] 
    param[:, i, :] = (quant_param[:, i, :] - zero_point[:, i // group_num, 0]) * scale[:, i // group_num, 0]
    return: param: [..., X ]
    '''
    return ((unsqueeze_from_6bit(quant_param) - zero_point) * scale).reshape(*quant_param.shape[:-2],-1)

def unsqueeze_from_6bit(quant_tensor: torch.Tensor):
    assert quant_tensor.shape[-1] % 3 == 0
    shape_tp = tuple(quant_tensor.shape)
    origin_tensor = torch.empty(quant_tensor.numel()//3*4, dtype=torch.uint8)
    quant_tensor = quant_tensor.flatten()
    origin_tensor[0::4] = torch.bitwise_and(quant_tensor[0::3], 0x3f)
    origin_tensor[1::4] = ((quant_tensor[1::3] & 0xf ) << 2) | (quant_tensor[0::3] >> 6)
    origin_tensor[2::4] = ((quant_tensor[2::3] & 0x3 ) << 4) | (quant_tensor[1::3] >> 4)
    origin_tensor[3::4] = quant_tensor[2::3] >> 2
    return origin_tensor.reshape(*shape_tp[:-1], -1)

def recover_from_quant(qweight_lst : list[tuple[str, torch.Tensor]]) -> list[tuple[str, torch.Tensor]]:
    '''
    a weight named `X` will be recoverd from `X.qweight`(uint8), `X.zero_point`(int8) and `X.scales`(float16)
    '''
    key_set = set()
    qweight_dic = {}
    res_lst = []
    for namei, ti in qweight_lst:
        if 'norm' not in namei:
            key_set.add(namei[:namei.rfind('.')])
            qweight_dic[namei] = ti
        else:
            res_lst.append((namei, ti))
    
    for ki in tqdm(key_set):
        qweighti = qweight_dic[ki+".qweight"]
        zero_pointi = qweight_dic[ki+".zero_point"]
        scalesi = qweight_dic[ki+".scales"]
        res_lst.append((ki, calculate_dequant(qweighti, zero_pointi, scalesi)))
    return res_lst