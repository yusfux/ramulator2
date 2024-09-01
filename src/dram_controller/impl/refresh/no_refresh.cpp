#include <vector>

#include "base/base.h"
#include "dram_controller/controller.h"
#include "dram_controller/refresh.h"

namespace Ramulator {

class NoRefresh : public IRefreshManager, public Implementation {
  RAMULATOR_REGISTER_IMPLEMENTATION(IRefreshManager, NoRefresh, "NoRefresh", "No Refresh scheme.")
  private:

  public:
    void init() override { 

    };

    void setup(IFrontEnd* frontend, IMemorySystem* memory_system) override {

    };

    void tick() {

    };

};

}       // namespace Ramulator
