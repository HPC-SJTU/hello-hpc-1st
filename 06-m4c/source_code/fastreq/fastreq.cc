#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>
#include <string>
#include <vector>
#include "src/fastreq"

// Python bytes
class PyBytes {
private:
    PyObject* py_bytes_;
    buf_mut span_;

public:
    PyBytes(): py_bytes_(nullptr) {}
    // Constructor that creates uninitialized bytes of given length
    explicit PyBytes(size_t length) {
        py_bytes_ = PyBytes_FromStringAndSize(nullptr, length);
        if (!py_bytes_) {
            throw std::runtime_error("Failed to create PyBytes object");
        }
        char* data = PyBytes_AS_STRING(py_bytes_);
        span_ = buf_mut(reinterpret_cast<std::byte*>(data), length);
    }
    
    // Constructor from existing PyObject*
    explicit PyBytes(PyObject* obj) : py_bytes_(obj) {
        if (!PyBytes_Check(obj)) {
            throw std::runtime_error("Object is not a PyBytes");
        }
        char* data = PyBytes_AS_STRING(obj);
        Py_ssize_t size = PyBytes_GET_SIZE(obj);
        span_ = buf_mut(reinterpret_cast<std::byte*>(data), size);
    }
    
    // Destructor
    ~PyBytes() {
        Py_XDECREF(py_bytes_);
    }
    
    // Move constructor
    PyBytes(PyBytes&& other) noexcept : py_bytes_(other.py_bytes_), span_(other.span_) {
        other.py_bytes_ = nullptr;
        other.span_ = buf_mut();
    }
    
    // Move assignment
    PyBytes& operator=(PyBytes&& other) noexcept {
        if (this != &other) {
            Py_XDECREF(py_bytes_);
            py_bytes_ = other.py_bytes_;
            span_ = other.span_;
            other.py_bytes_ = nullptr;
            other.span_ = buf_mut();
        }
        return *this;
    }
    
    // Copy constructor and assignment are deleted
    PyBytes(const PyBytes&) = delete;
    PyBytes& operator=(const PyBytes&) = delete;
    
    // Get the underlying PyObject
    PyObject* pyobject() const { return py_bytes_; }
    
    // Release ownership of PyObject
    PyObject* release() {
        PyObject* temp = py_bytes_;
        py_bytes_ = nullptr;
        span_ = buf_mut();
        return temp;
    }

    // implements Buf

    static PyBytes new_(std::size_t len) {
        return PyBytes(len);
    }
    
    buf span() const noexcept {
        return span_;
    }
    
    buf_mut span_mut() noexcept {
        return span_;
    }
};

static_assert(Buf<PyBytes>);

static PyObject* m4c_get(PyObject* /*self*/, PyObject* args) {
    PyObject* urls_list;
    uint16_t remote_port = 18080;
    
    if (!PyArg_ParseTuple(args, "O|H", &urls_list, &remote_port)) {
        return nullptr;
    }
    
    if (!PyList_Check(urls_list)) {
        PyErr_SetString(PyExc_TypeError, "urls must be a list of strings");
        return nullptr;
    }
    
    try {
        // Convert Python list to C++ vector
        std::vector<std::string> urls;
        Py_ssize_t size = PyList_Size(urls_list);
        urls.reserve(size);
        
        for (Py_ssize_t i = 0; i < size; ++i) {
            PyObject* item = PyList_GetItem(urls_list, i);
            if (!PyUnicode_Check(item)) {
                PyErr_SetString(PyExc_TypeError, "all urls must be strings");
                return nullptr;
            }
            
            Py_ssize_t len;
            const char* str = PyUnicode_AsUTF8AndSize(item, &len);
            if (!str) {
                return nullptr;
            }
            urls.emplace_back(str, len);
        }
        
        // Call the implementation
        auto results = fastreq<PyBytes>(std::move(urls), remote_port);
        
        // Convert results to Python list
        PyObject* result_list = PyList_New(results.size());
        if (!result_list) {
            return nullptr;
        }
        
        for (size_t i = 0; i < results.size(); ++i) {
            PyObject* bytes_obj = results[i].release();
            if (!bytes_obj) {
                Py_DECREF(result_list);
                return nullptr;
            }
            PyList_SET_ITEM(result_list, i, bytes_obj);
        }
        
        return result_list;
        
    } catch (const std::exception& e) {
        PyErr_SetString(PyExc_RuntimeError, e.what());
        return nullptr;
    }
}

// Module method table
static PyMethodDef FastReqMethods[] = {
    {"get", m4c_get, METH_VARARGS, 
     "Perform batch HTTP 1.1 get from localhost:[remote_port][url].\n\n"
     "It assumes remote is exactly the m4c server, and cannot used on any normal HTTP server."},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef fastreqmodule = {
    PyModuleDef_HEAD_INIT,
    "fastreq",
    "Fast batch HTTP client for m4c server",
    -1,
    FastReqMethods
};

PyMODINIT_FUNC PyInit_fastreq() {
    return PyModule_Create(&fastreqmodule);
}