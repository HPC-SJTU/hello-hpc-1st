#ifndef Q_6BIT_H
#define Q_6BIT_H

#include <torch/script.h>

at::Tensor unsqueeze_from_6bit(const at::Tensor& qweight);
at::Tensor calculate_dequant(
    const at::Tensor& qweight, 
    const at::Tensor& zero_point,
    const at::Tensor& scale
);

#endif  // Q_6BIT_H
