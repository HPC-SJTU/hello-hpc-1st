#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <random>
#include <algorithm>
#include <iomanip>
#include <fstream>
#include <sstream>

class OceanSimulation {
private:
    int width, height, depth;

    int target_iteration;
    
    std::vector<std::vector<std::vector<double>>> temperature;
    std::vector<std::vector<std::vector<double>>> salinity;
    std::vector<std::vector<std::vector<double>>> velocity_x;
    std::vector<std::vector<std::vector<double>>> velocity_y;
    std::vector<std::vector<std::vector<double>>> velocity_z;
    std::vector<std::vector<std::vector<double>>> pressure;

    std::vector<std::vector<std::vector<double>>> tmp_temperature;
    std::vector<std::vector<std::vector<double>>> tmp_salinity;
    std::vector<std::vector<std::vector<double>>> tmp_velocity_x;
    std::vector<std::vector<std::vector<double>>> tmp_velocity_y;
    std::vector<std::vector<std::vector<double>>> tmp_velocity_z;
    std::vector<std::vector<std::vector<double>>> tmp_pressure;
    
    
    void loadTemperatureData(const std::string& line) {
        std::istringstream iss(line);
        int i, j, k;
        double temp;
        if (iss >> i >> j >> k >> temp) {
            if (i >= 0 && i < width && j >= 0 && j < height && k >= 0 && k < depth) {
                temperature[i][j][k] = temp;
            }
        }
    }
    
    void loadSalinityData(const std::string& line) {
        std::istringstream iss(line);
        int i, j, k;
        double salt;
        if (iss >> i >> j >> k >> salt) {
            if (i >= 0 && i < width && j >= 0 && j < height && k >= 0 && k < depth) {
                salinity[i][j][k] = salt;
            }
        }
    }
    
    void loadVelocityData(const std::string& line) {
        std::istringstream iss(line);
        int i, j, k;
        double vx, vy, vz;
        if (iss >> i >> j >> k >> vx >> vy >> vz) {
            if (i >= 0 && i < width && j >= 0 && j < height && k >= 0 && k < depth) {
                velocity_x[i][j][k] = vx;
                velocity_y[i][j][k] = vy;
                velocity_z[i][j][k] = vz;
            }
        }
    }
    
    void loadPressureData(const std::string& line) {
        std::istringstream iss(line);
        int i, j, k;
        double press;
        if (iss >> i >> j >> k >> press) {
            if (i >= 0 && i < width && j >= 0 && j < height && k >= 0 && k < depth) {
                pressure[i][j][k] = press;
            }
        }
    }
    
    std::string getCurrentTimeString() {
        auto now = std::chrono::system_clock::now();
        auto time_t = std::chrono::system_clock::to_time_t(now);
        std::stringstream ss;
        ss << std::put_time(std::localtime(&time_t), "%Y-%m-%d %H:%M:%S");
        return ss.str();
    }
    
    void outputStatisticsSection(std::ofstream& file) {
        double avg_temp = 0.0, min_temp = temperature[0][0][0], max_temp = temperature[0][0][0];
        double avg_salinity = 0.0, min_salinity = salinity[0][0][0], max_salinity = salinity[0][0][0];
        double max_velocity = 0.0, avg_velocity = 0.0;
        double avg_pressure = 0.0, min_pressure = pressure[0][0][0], max_pressure = pressure[0][0][0];
        
        int total_points = width * height * depth;
        
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    avg_temp += temperature[i][j][k];
                    min_temp = std::min(min_temp, temperature[i][j][k]);
                    max_temp = std::max(max_temp, temperature[i][j][k]);
                    
                    avg_salinity += salinity[i][j][k];
                    min_salinity = std::min(min_salinity, salinity[i][j][k]);
                    max_salinity = std::max(max_salinity, salinity[i][j][k]);
                    
                    double vel_mag = std::sqrt(velocity_x[i][j][k] * velocity_x[i][j][k] + 
                                             velocity_y[i][j][k] * velocity_y[i][j][k] + 
                                             velocity_z[i][j][k] * velocity_z[i][j][k]);
                    avg_velocity += vel_mag;
                    max_velocity = std::max(max_velocity, vel_mag);
                    
                    avg_pressure += pressure[i][j][k];
                    min_pressure = std::min(min_pressure, pressure[i][j][k]);
                    max_pressure = std::max(max_pressure, pressure[i][j][k]);
                }
            }
        }
        
        avg_temp /= total_points;
        avg_salinity /= total_points;
        avg_velocity /= total_points;
        avg_pressure /= total_points;
        
        file << "[STATISTICS]\n";
        file << "# 海洋模拟统计信息\n";
        file << "TEMPERATURE_AVG " << std::fixed << std::setprecision(10) << avg_temp << "\n";
        file << "TEMPERATURE_MIN " << min_temp << "\n";
        file << "TEMPERATURE_MAX " << max_temp << "\n";
        file << "SALINITY_AVG " << avg_salinity << "\n";
        file << "SALINITY_MIN " << min_salinity << "\n";
        file << "SALINITY_MAX " << max_salinity << "\n";
        file << "VELOCITY_AVG " << avg_velocity << "\n";
        file << "VELOCITY_MAX " << max_velocity << "\n";
        file << "PRESSURE_AVG " << avg_pressure << "\n";
        file << "PRESSURE_MIN " << min_pressure << "\n";
        file << "PRESSURE_MAX " << max_pressure << "\n\n";
    }
    
    void outputSamplePointsSection(std::ofstream& file) {
        file << "[SAMPLE_POINTS]\n";
        file << "# 格式: 位置名称 [i,j,k] 温度 盐度 速度_x 速度_y 速度_z 压力\n";
        
        int sample_points[][3] = {
            {width/4, height/4, 0},      
            {width/2, height/2, 0},      
            {3*width/4, 3*height/4, 0},  
            {width/2, height/2, depth/4}, 
            {width/2, height/2, depth/2}, 
            {width/2, height/2, depth-1}  
        };
        
        const char* point_names[] = {
            "Surface_Point_1", "Surface_Center", "Surface_Point_2", 
            "Mid_Layer", "Deep_Layer", "Bottom_Layer"
        };
        
        for (int p = 0; p < 6; p++) {
            int i = sample_points[p][0];
            int j = sample_points[p][1];
            int k = sample_points[p][2];
            
            file << point_names[p] << " [" << i << "," << j << "," << k << "] "
                 << std::fixed << std::setprecision(10) 
                 << temperature[i][j][k] << " "
                 << salinity[i][j][k] << " "
                 << velocity_x[i][j][k] << " "
                 << velocity_y[i][j][k] << " "
                 << velocity_z[i][j][k] << " "
                 << pressure[i][j][k] << "\n";
        }
        file << "\n";
    }
    
    void outputTemperatureSection(std::ofstream& file) {
        file << "[TEMPERATURE_FIELD]\n";
        file << "# 格式: i j k temperature\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << temperature[i][j][k] << "\n";
                }
            }
        }
        file << "\n";
    }
    
    void outputSalinitySection(std::ofstream& file) {
        file << "[SALINITY_FIELD]\n";
        file << "# 格式: i j k salinity\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << salinity[i][j][k] << "\n";
                }
            }
        }
        file << "\n";
    }
    
    void outputVelocitySection(std::ofstream& file) {
        file << "[VELOCITY_FIELD]\n";
        file << "# 格式: i j k vx vy vz magnitude\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    double magnitude = std::sqrt(velocity_x[i][j][k] * velocity_x[i][j][k] + 
                                               velocity_y[i][j][k] * velocity_y[i][j][k] + 
                                               velocity_z[i][j][k] * velocity_z[i][j][k]);
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << velocity_x[i][j][k] << " "
                         << velocity_y[i][j][k] << " "
                         << velocity_z[i][j][k] << " "
                         << magnitude << "\n";
                }
            }
        }
        file << "\n";
    }
    
    void outputPressureSection(std::ofstream& file) {
        file << "[PRESSURE_FIELD]\n";
        file << "# 格式: i j k pressure\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << pressure[i][j][k] << "\n";
                }
            }
        }
        file << "\n";
    }

    template <typename T>
    void allocate3DVector(std::vector<std::vector<std::vector<T>>>& vec, int w, int h, int d, T initValue) {
        vec.clear();
        vec.reserve(w); 
        for (int i = 0; i < w; ++i) {
            vec.emplace_back(); 
            vec[i].reserve(h); 
            for (int j = 0; j < h; ++j) {
                vec[i].emplace_back(d, initValue);
            }
        }
    }
    
    
public:
    OceanSimulation(int w, int h, int d) : width(w), height(h), depth(d) {
        initializeFields();
    }

    void initializeFields() {
        allocate3DVector(temperature, width, height, depth, 0.0);
        allocate3DVector(salinity, width, height, depth, 0.0);
        allocate3DVector(velocity_x, width, height, depth, 0.0);
        allocate3DVector(velocity_y, width, height, depth, 0.0);
        allocate3DVector(velocity_z, width, height, depth, 0.0);
        allocate3DVector(pressure, width, height, depth, 0.0);
        allocate3DVector(tmp_temperature, width, height, depth, 0.0);
        allocate3DVector(tmp_salinity, width, height, depth, 0.0);
        allocate3DVector(tmp_velocity_x, width, height, depth, 0.0);
        allocate3DVector(tmp_velocity_y, width, height, depth, 0.0);
        allocate3DVector(tmp_velocity_z, width, height, depth, 0.0);
        allocate3DVector(tmp_pressure, width, height, depth, 0.0);
    }

    bool loadFromFile(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) {
            std::cerr << "无法打开输入文件: " << filename << std::endl;
            return false;
        }
        
        std::string line;
        std::string section;
        
        while (std::getline(file, line)) {
            if (line.empty() || line[0] == '#') continue;
            
            if (line.find("[") != std::string::npos && line.find("]") != std::string::npos) {
                section = line;
                continue;
            }
            
            if (section == "[GRID_SIZE]") {
                std::istringstream iss(line);
                iss >> width >> height >> depth;
                initializeFields();
            }
            else if (section == "[TARGET_ITERATION]") {
                std::istringstream iss(line);
                iss >> target_iteration;
            }
            else if (section == "[TEMPERATURE_DATA]") {
                loadTemperatureData(line);
            }
            else if (section == "[SALINITY_DATA]") {
                loadSalinityData(line);
            }
            else if (section == "[VELOCITY_DATA]") {
                loadVelocityData(line);
            }
            else if (section == "[PRESSURE_DATA]") {
                loadPressureData(line);
            }
        }
        
        file.close();
        std::cout << "成功从文件加载初始化数据: " << filename << std::endl;
        return true;
    }
    
    void outputToFile(const std::string& filename) {
        std::ofstream file(filename);
        if (!file.is_open()) {
            std::cerr << "无法创建输出文件: " << filename << std::endl;
            return;
        }
        
        file << "# 海洋模拟结果数据文件\n";
        file << "# 生成时间: " << getCurrentTimeString() << "\n";
        file << "# 网格尺寸: " << width << " x " << height << " x " << depth << "\n";
        file << "# 总网格点数: " << (width * height * depth) << "\n\n";
        
        outputStatisticsSection(file);
        
        outputSamplePointsSection(file);
        
        outputTemperatureSection(file);
        outputSalinitySection(file);
        outputVelocitySection(file);
        outputPressureSection(file);
        
        file.close();
        std::cout << "所有数据已输出到文件: " << filename << std::endl;
    }
    
    void generateInputTemplate(const std::string& filename) {
        std::ofstream file(filename);
        if (!file.is_open()) {
            std::cerr << "无法创建输入文件: " << filename << std::endl;
            return;
        }
        
        file << "# 海洋模拟输入参数文件\n";
        file << "# 格式说明：每个节以[节名]开始，数据紧随其后\n\n";
        
        file << "[GRID_SIZE]\n";
        file << "# 格式: width height depth\n";
        file << width << " " << height << " " << depth << "\n\n";
        
        file << "[TEMPERATURE_DATA]\n";
        file << "# 格式: i j k temperature\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << temperature[i][j][k] << "\n";
                }
            }
        }
        file << "\n";
        
        file << "[SALINITY_DATA]\n";
        file << "# 格式: i j k salinity\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << salinity[i][j][k] << "\n";
                }
            }
        }
        file << "\n";
        
        file << "[VELOCITY_DATA]\n";
        file << "# 格式: i j k vx vy vz\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << velocity_x[i][j][k] << " "
                         << velocity_y[i][j][k] << " "
                         << velocity_z[i][j][k] << "\n";
                }
            }
        }
        file << "\n";
        
        file << "[PRESSURE_DATA]\n";
        file << "# 格式: i j k pressure\n";
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    file << i << " " << j << " " << k << " " 
                         << std::fixed << std::setprecision(10) 
                         << pressure[i][j][k] << "\n";
                }
            }
        }
        
        file.close();
        std::cout << "输入文件模板已生成: " << filename << std::endl;
    }
    
    void initializeVelocityField() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis_xy(-0.01, 0.01); 
        std::uniform_real_distribution<> dis_z(-0.001, 0.001); 
        
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    velocity_x[i][j][k] = dis_xy(gen);
                    velocity_y[i][j][k] = dis_xy(gen);
                    velocity_z[i][j][k] = dis_z(gen);
                    if (k == depth - 1) {
                        velocity_x[i][j][k] = 0.0;
                        velocity_y[i][j][k] = 0.0;
                        velocity_z[i][j][k] = 0.0;
                    }
                }
            }
        }
    }

    void initializeTemperatureField() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(15.0, 25.0);
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    double depth_factor = 1.0 - static_cast<double>(k) / depth;
                    temperature[i][j][k] = dis(gen) * depth_factor + 2.0;
                }
            }
        }
    }
    
    void initializeSalinityField() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(30.0, 40.0);
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    salinity[i][j][k] = dis(gen);
                }
            }
        }
    }
    
    void initializePressureField() {
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    pressure[i][j][k] = 101325.0 + k * 1000.0 * 9.81;
                }
            }
        }
    }
    
    void computeHeatDiffusion(double dt, double thermal_diffusivity) {
        performHeatDiffusionStep(dt, thermal_diffusivity);
    }
    
    void performHeatDiffusionStep(double dt, double thermal_diffusivity) {
        applyHeatDiffusionEquation(dt, thermal_diffusivity);
    }
    
    void applyHeatDiffusionEquation(double dt, double thermal_diffusivity) {
        tmp_temperature = temperature;
        
        for (int i = 1; i < width - 1; i++) {
            for (int j = 1; j < height - 1; j++) {
                for (int k = 1; k < depth - 1; k++) {
                    double laplacian = 0.0;
                    laplacian += temperature[i+1][j][k] - 2.0 * temperature[i][j][k] + temperature[i-1][j][k];
                    laplacian += temperature[i][j+1][k] - 2.0 * temperature[i][j][k] + temperature[i][j-1][k];
                    laplacian += temperature[i][j][k+1] - 2.0 * temperature[i][j][k] + temperature[i][j][k-1];
                    tmp_temperature[i][j][k] = temperature[i][j][k] + dt * thermal_diffusivity * laplacian;
                    double nonlinear_term = 0.0;
                    for (int di = -1; di <= 1; di++) {
                        for (int dj = -1; dj <= 1; dj++) {
                            for (int dk = -1; dk <= 1; dk++) {
                                if (di == 0 && dj == 0 && dk == 0) continue;
                                double weight = 1.0 / (std::abs(di) + std::abs(dj) + std::abs(dk));
                                nonlinear_term += weight * std::sin(temperature[i+di][j+dj][k+dk] * 0.1);
                            }
                        }
                    }
                    tmp_temperature[i][j][k] += dt * 0.001 * nonlinear_term;
                }
            }
        }
        temperature = tmp_temperature;
    }
    
    void computeOceanCurrent(double dt) {
        updateCurrentField(dt);
    }
    
    void updateCurrentField(double dt) {
        calculateVelocityComponents(dt);
    }
    
    void calculateVelocityComponents(double dt) {

        tmp_velocity_x = velocity_x;
        tmp_velocity_y = velocity_y;

        for (int i = 1; i < width - 1; i++) {
            for (int j = 1; j < height - 1; j++) {
                for (int k = 1; k < depth - 1; k++) {
                    double temp_grad_x = (temperature[i+1][j][k] - temperature[i-1][j][k]) * 0.5;
                    double temp_grad_y = (temperature[i][j+1][k] - temperature[i][j-1][k]) * 0.5;
                    double salt_grad_x = (salinity[i+1][j][k] - salinity[i-1][j][k]) * 0.5;
                    double salt_grad_y = (salinity[i][j+1][k] - salinity[i][j-1][k]) * 0.5;
                    
                    double density_grad_x = -0.2 * temp_grad_x + 0.8 * salt_grad_x;
                    double density_grad_y = -0.2 * temp_grad_y + 0.8 * salt_grad_y;

                    double coeff = dt * 0.001; 
                    
                    tmp_velocity_x[i][j][k] += coeff * density_grad_y;
                    tmp_velocity_y[i][j][k] += coeff * density_grad_x;
                    
                    double visc_coeff = dt * 0.0001;
                    tmp_velocity_x[i][j][k] += visc_coeff * (tmp_velocity_x[i+1][j][k] - 2.0 * tmp_velocity_x[i][j][k] + tmp_velocity_x[i-1][j][k]);
                    tmp_velocity_y[i][j][k] += visc_coeff * (tmp_velocity_y[i+1][j][k] - 2.0 * tmp_velocity_y[i][j][k] + tmp_velocity_y[i-1][j][k]);
                }
            }
        }
        velocity_x = tmp_velocity_x;
        velocity_y = tmp_velocity_y;
    }

    double computeTurbulentViscosity(int i, int j, int k) {
        double du_dx = velocity_x[i+1][j][k] - velocity_x[i-1][j][k];
        double dv_dy = velocity_y[i][j+1][k] - velocity_y[i][j-1][k];
        return 0.0001 * (du_dx * du_dx + dv_dy * dv_dy);
    }

    void processSalinityDiffusion(double dt) {
        tmp_salinity = salinity;
        for (int i = 1; i < width - 1; i++) {
            for (int j = 1; j < height - 1; j++) {
                for (int k = 1; k < depth - 1; k++) {
                    double advection = velocity_x[i][j][k] * (salinity[i+1][j][k] - salinity[i-1][j][k]) * 0.5;
                    tmp_salinity[i][j][k] = salinity[i][j][k] - dt * 0.1 * advection;
                    double diffusion = dt * 0.0001 * (salinity[i+1][j][k] - 2.0 * salinity[i][j][k] + salinity[i-1][j][k]);
                    tmp_salinity[i][j][k] += diffusion;
                }
            }
        }
        salinity = tmp_salinity;
    }

    void applyTurbulentDiffusion(int i, int j, int k, double dt, double viscosity) {
        tmp_velocity_x = velocity_x;
        tmp_velocity_y = velocity_y;
        
        if (i > 0 && i < width-1 && j > 0 && j < height-1 && k > 0 && k < depth-1) {
            double laplacian_u = velocity_x[i+1][j][k] - 2.0 * velocity_x[i][j][k] + velocity_x[i-1][j][k];
            double laplacian_v = velocity_y[i+1][j][k] - 2.0 * velocity_y[i][j][k] + velocity_y[i-1][j][k];
            tmp_velocity_x[i][j][k] = velocity_x[i][j][k] + dt * viscosity * laplacian_u;
            tmp_velocity_y[i][j][k] = velocity_y[i][j][k] + dt * viscosity * laplacian_v;
        }

        velocity_x = tmp_velocity_x;
        velocity_y = tmp_velocity_y;
    }
    
    void computeWavePropagation(double dt) {
        calculateWaveHeight(dt);
    }
    
    void calculateWaveHeight(double dt) {
        updateWaveField(dt);
    }
    
    void updateWaveField(double dt) {
        for (int i = 1; i < width - 1; i++) {
            for (int j = 1; j < height - 1; j++) {
                double wave_speed = 5.0;
                double wave_height = std::sin(0.1 * i + 0.1 * j + dt * wave_speed);
                temperature[i][j][0] += 0.1 * wave_height;
            }
        }
    }
    
    void computeTopographicEffect() {
        processSeafloorInfluence();
    }
    
    void processSeafloorInfluence() {
        applyBottomBoundaryCondition();
    }
    
    void applyBottomBoundaryCondition() {
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                velocity_x[i][j][depth-1] = 0.0;
                velocity_y[i][j][depth-1] = 0.0;
                velocity_z[i][j][depth-1] = 0.0;
            }
        }
    }
    
    void computeAtmosphericCoupling() {
        calculateHeatFlux();
    }
    
    void calculateHeatFlux() {
        processAtmosphericForcing();
    }
    
    void processAtmosphericForcing() {
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                double heat_flux = 100.0 * std::sin(0.01 * i) * std::cos(0.01 * j);
                temperature[i][j][0] += 0.001 * heat_flux;
            }
        }
    }
    
    void computeTidalEffect(double time) {
        calculateTidalForce(time);
    }
    
    void calculateTidalForce(double time) {
        applyTidalCorrection(time);
    }
    
    void applyTidalCorrection(double time) {
        double tidal_amplitude = 0.5;
        double tidal_frequency = 2.0 * M_PI / 12.42;
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                double tidal_elevation = tidal_amplitude * std::sin(tidal_frequency * time);
                pressure[i][j][0] += 1000.0 * 9.81 * tidal_elevation;
            }
        }
    }
    
    void computeSalinityTransport(double dt) {
        calculateSaltAdvection(dt);
    }
    
    void calculateSaltAdvection(double dt) {
        processSalinityDiffusion(dt);
    }
    
    void computeMixedLayerDepth() {
        calculateMixingDepth();
    }
    
    void calculateMixingDepth() {
        determineMixedLayerBoundary();
    }
    
    void determineMixedLayerBoundary() {
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                double surface_temp = temperature[i][j][0];
                for (int k = 1; k < depth; k++) {
                    if (std::abs(temperature[i][j][k] - surface_temp) > 0.2) {
                        break;
                    }
                }
            }
        }
    }
    
    void runSimulation() {
        
        double dt = 0.1;
        
        for (int t = 0; t < target_iteration; t++) {
            double current_time = t * dt;
            computeHeatDiffusion(dt, 1.0e-6);
            computeOceanCurrent(dt);
            computeWavePropagation(dt);
            computeTopographicEffect();
            computeAtmosphericCoupling();
            computeTidalEffect(current_time);
            computeSalinityTransport(dt);
            computeMixedLayerDepth();
            if (t % 10 == 0) {
                bool has_nan = checkForNaN();
                if (has_nan) {
                    std::cout << "警告：在第 " << t << " 步检测到NaN值，停止模拟" << std::endl;
                    break;
                }
                std::cout << "Time step: " << t << "/" << target_iteration << std::endl;
            }
        }
    }

    bool checkForNaN() {
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    if (std::isnan(temperature[i][j][k]) || std::isnan(salinity[i][j][k]) ||
                        std::isnan(velocity_x[i][j][k]) || std::isnan(velocity_y[i][j][k]) ||
                        std::isnan(velocity_z[i][j][k]) || std::isnan(pressure[i][j][k])) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    void printStatistics() {
        double avg_temp = 0.0;
        double max_velocity = 0.0;
        
        for (int i = 0; i < width; i++) {
            for (int j = 0; j < height; j++) {
                for (int k = 0; k < depth; k++) {
                    avg_temp += temperature[i][j][k];
                    double vel_mag = std::sqrt(velocity_x[i][j][k] * velocity_x[i][j][k] + 
                                             velocity_y[i][j][k] * velocity_y[i][j][k] + 
                                             velocity_z[i][j][k] * velocity_z[i][j][k]);
                    max_velocity = std::max(max_velocity, vel_mag);
                }
            }
        }
        
        avg_temp /= (width * height * depth);
        std::cout << "Average temperature: " << avg_temp << "°C" << std::endl;
        std::cout << "Maximum velocity: " << max_velocity << " m/s" << std::endl;
    }

    void printSampleData() {
        std::cout << "\n=== 采样点数据 ===" << std::endl;
        
        int sample_points[][3] = {
            {width/4, height/4, 0},      
            {width/2, height/2, 0},      
            {3*width/4, 3*height/4, 0},  
            {width/2, height/2, depth/4}, 
            {width/2, height/2, depth/2}, 
            {width/2, height/2, depth-1} 
        };
        
        const char* point_names[] = {
            "表层点1", "表层中心", "表层点2", "中层点", "深层点", "底层点"
        };
        
        for (int p = 0; p < 6; p++) {
            int i = sample_points[p][0];
            int j = sample_points[p][1];
            int k = sample_points[p][2];
            
            std::cout << point_names[p] << " [" << i << "," << j << "," << k << "]:" << std::endl;
            std::cout << "  温度: " << std::fixed << std::setprecision(10) << temperature[i][j][k] << "°C" << std::endl;
            std::cout << "  盐度: " << std::fixed << std::setprecision(10) << salinity[i][j][k] << "‰" << std::endl;
            std::cout << "  速度: (" << std::fixed << std::setprecision(10) 
                    << velocity_x[i][j][k] << ", " 
                    << velocity_y[i][j][k] << ", " 
                    << velocity_z[i][j][k] << ") m/s" << std::endl;
            std::cout << "  压力: " << std::fixed << std::setprecision(10) << pressure[i][j][k] << " Pa" << std::endl;
            std::cout << std::endl;
        }
    }
};

int main(int argc, char* argv[]) {
    std::cout << "=== 海洋温度场仿真程序 ===" << std::endl;
    
    OceanSimulation ocean(100, 100, 50);
    
    std::cout << "从输入文件加载初始条件: " << "OceanSimInput.txt"<< std::endl;
    if (!ocean.loadFromFile("OceanSimInput.txt")) {
        std::cout << "使用默认初始化..." << std::endl;
    }
    
    std::cout << "开始仿真..." << std::endl;
    auto start_time = std::chrono::high_resolution_clock::now();
    
    ocean.runSimulation();
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time);
    
    std::cout << "仿真完成！" << std::endl;
    std::cout << "总耗时: " << duration.count() << " ms" << std::endl;
    
    ocean.printStatistics();
    ocean.printSampleData();
    
    std::cout << "\n正在输出结果数据..." << std::endl;
    ocean.outputToFile("OceanSimOutput.txt");
    std::cout << "数据输出完成！" << std::endl;
    
    return 0;
}