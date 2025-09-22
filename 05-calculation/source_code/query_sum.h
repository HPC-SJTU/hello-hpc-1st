#ifndef QUERY_SUM_H
#define QUERY_SUM_H
size_t sum(short A[], size_t n, size_t m, double k) {
    size_t answer = 0;
    for (size_t i = 1; i <= n; ++i) {
        size_t j_limit = std::pow(i, k);
        double sum = 0.0;
        for (size_t j = 1; j <= j_limit; ++j) {
            if (A[i * m + j] % 2) answer += A[i * m + j];
            else answer += (A[i * m + j] << 1);
            double sum_sin = 0.0;
            for (size_t p = 1; p <= j; ++p) 
                sum_sin += std::sin(p) * std::cos(p);
            sum += j * sum_sin * std::sin(j);
        }
        answer -= size_t(sum);
    }
    return answer;
}
#endif // QUERY_SUM_H