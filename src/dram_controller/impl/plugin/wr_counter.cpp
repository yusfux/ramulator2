#include <vector>
#include <unordered_map>
#include <limits>
#include <random>
#include <filesystem>
#include <fstream>

#include "base/base.h"
#include "dram_controller/controller.h"
#include "dram_controller/plugin.h"

namespace Ramulator {

class WriteCounter : public IControllerPlugin, public Implementation {
  RAMULATOR_REGISTER_IMPLEMENTATION(IControllerPlugin, WriteCounter, "WriteCounter", "Counting the total number of writes to each cacheline.")

  private:
    IDRAM* m_dram = nullptr;

    std::unordered_map<int, int> m_write_counters;
    std::filesystem::path m_save_path; 


  public:
    void init() override { 
      m_save_path = param<std::string>("path").desc("Path to the trace file").required();
      auto parent_path = m_save_path.parent_path();
      std::filesystem::create_directories(parent_path);
      if (!(std::filesystem::exists(parent_path) && std::filesystem::is_directory(parent_path))) {
        throw ConfigurationError("Invalid path to trace file: {}", parent_path.string());
      }
    };

    void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override {
      m_ctrl = cast_parent<IDRAMController>();
      m_dram = m_ctrl->m_dram;
    };

    void update(bool request_found, ReqBuffer::iterator& req_it) override {
      if (request_found && m_dram->m_commands("WR") == req_it->command) {
        // it is safe to assume that the values inside unoredered_map are initialized to 0 according to cpp standart [ref]
        m_write_counters[req_it->addr]++;
      }
    };

    void finalize() override {
      std::ofstream output(m_save_path);
      for (const auto& [addr, count] : m_write_counters) {
        output << fmt::format("{}, {}", addr, count) << std::endl;
      }
      output.close();
    }

};

}       // namespace Ramulator
