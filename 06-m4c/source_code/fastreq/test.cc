// Claude AI Assistant - Copyright (c) 2025 Anthropic PBC. All rights reserved.
#include "src/fastreq"
#include <iostream>
#include <chrono>
#include <cstdint>
#include <cassert>

using byte = std::byte;

// VectorBuf wrapper class
class VectorBuf {
public:
    vector<byte> data_;
    // Default constructor
    VectorBuf() = default;

    // Constructor from existing vector
    VectorBuf(vector<byte> data) : data_(std::move(data)) {}

    // Move constructor
    VectorBuf(VectorBuf&& other) noexcept : data_(std::move(other.data_)) {}
    
    // Move assignment operator
    VectorBuf& operator=(VectorBuf&& other) noexcept {
        if (this != &other) {
            data_ = std::move(other.data_);
        }
        return *this;
    }
    
    // Copy constructor
    VectorBuf(const VectorBuf& other) : data_(other.data_) {}
    
    // Copy assignment operator
    VectorBuf& operator=(const VectorBuf& other) {
        if (this != &other) {
            data_ = other.data_;
        }
        return *this;
    }
    
    static VectorBuf new_(size_t len) { return VectorBuf(std::move(vector<byte>(len))); }
    
    // Get immutable span - required by Buf concept
    buf span() const { return buf(data_.data(), data_.size()); }
    
    // Get mutable span - required by Buf concept  
    buf_mut span_mut() { return buf_mut(data_.data(), data_.size()); }
};

constexpr int CASES = 400000;
constexpr char CASEBASE[] = "/2/";

// Test function
void test_fastreq() {
    std::cout << "Starting fastreq test...\n";
    
    // Generate test URLs: ["/0/0", "/0/1", "/0/2", ..., "/0/1023"]
    std::vector<std::string> urls;
    urls.reserve(CASES);
    
    for (int i = 0; i < CASES; ++i) {
        urls.push_back(CASEBASE + std::to_string(i));
    }
    
    std::string remote = "localhost:18080";
    
    std::cout << "Generated " << urls.size() << " URLs\n";
    std::cout << "Remote endpoint: " << remote << "\n";
    
    // Measure execution time
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Call fastreq function
    std::vector<VectorBuf> responses = fastreq<VectorBuf>(urls, remote);
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    // Verify results
    std::cout << "Received " << responses.size() << " responses\n";
    std::cout << "Execution time: " << duration.count() << " ms\n";
    
    // Basic assertions
    assert(responses.size() == urls.size());
    assert(responses.size() == CASES);
    
    // Test first few responses
    for (size_t i = 0; i < std::min(size_t(5), responses.size()); ++i) {
        const auto& response = responses[i];
        auto span = response.span();
        
        std::cout << "Response " << i << " size: " << span.size() << " bytes\n";
        
        assert(!response.data_.empty());
        assert(span.size() > 0);
    }
    
    // Test last few responses
    std::cout << "\nLast few responses:\n";
    for (size_t i = responses.size() - 3; i < responses.size(); ++i) {
        const auto& response = responses[i];
        auto span = response.span();
        
        std::cout << "Response " << i << " size: " << span.size() << " bytes\n";
        
        // Check that response is not empty
        assert(!response.data_.empty());
        assert(span.size() > 0);
    }
    
    // Performance metrics
    double avg_time_per_request = double(duration.count()) / responses.size();
    std::cout << "\nPerformance metrics:\n";
    std::cout << "Average time per request: " << avg_time_per_request << " ms\n";
    std::cout << "Requests per second: " << (1000.0 / avg_time_per_request) << "\n";
    
    // Memory usage estimate
    size_t total_response_bytes = 0;
    for (const auto& response : responses) {
        total_response_bytes += response.data_.size();
    }
    
    std::cout << "Total response data: " << total_response_bytes << " bytes ("
              << (total_response_bytes / 1024.0) << " KB)\n";
    std::cout << "Average response size: " << (total_response_bytes / responses.size()) << " bytes\n";
    
    std::cout << "\n✅ All tests passed!\n";
}

int main() {
    try {
        test_fastreq();
        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "❌ Test failed with exception: " << e.what() << std::endl;
        return 1;
    }
    catch (...) {
        std::cerr << "❌ Test failed with unknown exception\n";
        return 1;
    }
}