#include "q6bit.h"
#include <torch/extension.h>
#include <iostream>

at::Tensor unsqueeze_from_6bit(const at::Tensor& qweight){
    return at::empty_like(qweight);
}

at::Tensor calculate_dequant(
    const at::Tensor& quant_param, 
    const at::Tensor& zero_point, 
    const at::Tensor& scale
) {
    return at::empty_like(quant_param);
}


// 绑定到Python
PYBIND11_MODULE(_C, m) {
    m.def("unsqueeze_from_6bit", &unsqueeze_from_6bit, 
        "unsqueeze from 6bit");
    m.def("calculate_dequant", &calculate_dequant,
        "calculate dequant");
}
