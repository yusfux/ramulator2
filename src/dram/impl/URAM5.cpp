#include "dram/dram.h"
#include "dram/lambdas.h"

namespace Ramulator {

class URAM5 : public IDRAM, public Implementation {
  RAMULATOR_REGISTER_IMPLEMENTATION(IDRAM, URAM5, "URAM5", "DDR5 based ULTRARAM Device Model")

  public:
    inline static const std::map<std::string, Organization> org_presets = {
      // name            density   DQ  Ch Ra Bg Ba   Ro     Co
      {"URAM5_8Gb_x4",   {8<<10,   4,  {1, 1, 8, 2, 1<<16, 1<<11}}},
      {"URAM5_8Gb_x8",   {8<<10,   8,  {1, 1, 8, 2, 1<<16, 1<<10}}},
      {"URAM5_8Gb_x16",  {8<<10,   16, {1, 1, 4, 2, 1<<16, 1<<10}}},
      {"URAM5_16Gb_x4",  {16<<10,  4,  {1, 1, 8, 4, 1<<16, 1<<11}}},
      {"URAM5_16Gb_x8",  {16<<10,  8,  {1, 1, 8, 4, 1<<16, 1<<10}}},
      {"URAM5_16Gb_x16", {16<<10,  16, {1, 1, 4, 4, 1<<16, 1<<10}}},
      {"URAM5_32Gb_x4",  {32<<10,  4,  {1, 1, 8, 4, 1<<17, 1<<11}}},
      {"URAM5_32Gb_x8",  {32<<10,  8,  {1, 1, 8, 4, 1<<17, 1<<10}}},
      {"URAM5_32Gb_x16", {32<<10,  16, {1, 1, 4, 4, 1<<17, 1<<10}}},
    };

    inline static const std::map<std::string, std::vector<int>> timing_presets = {
      // name           rate   nBL  nCL nRCD  nRP  nRPRD nRAS  nRC   nWR  nRTP nCWL nPPD nCCDS nCCDS_WR nCCDS_WTR nCCDL nCCDL_WR nCCDL_WTR nRRDS nRRDL nFAW nCS, tCK_ps
      {"URAM5_3200AN",  {3200,  8,  24,  24,  24,  24,   52,   75,   48,   12,  22,  2,    8,     8,     22+8+4,    8,     16,    22+8+16,   8,   -1,   -1,  2,   625}},
      {"URAM5_3200BN",  {3200,  8,  26,  26,  26,  26,   52,   77,   48,   12,  24,  2,    8,     8,     24+8+4,    8,     16,    24+8+16,   8,   -1,   -1,  2,   625}},
      {"URAM5_3200C",   {3200,  8,  28,  28,  28,  28,   52,   79,   48,   12,  26,  2,    8,     8,     26+8+4,    8,     16,    26+8+16,   8,   -1,   -1,  2,   625}},
      {"URAM5_8800AN",  {8800,  8,  62,  62,  62,  62,  141,  217,  133,   34,  60,  4,    8,     8,     60+8+9,   23,     89,    60+8+45,   8,   -1,   -1,  2,   227}} 
    };

    inline static const std::map<std::string, std::vector<double>> voltage_presets = {
      // name      VDD  VPP
      {"Default", {1.1, 1.8}},
    };

    inline static const std::map<std::string, std::vector<double>> current_presets = {
      // name     IDD0  IDD2N  IDD3N  IDD4R  IDD4W  IDD5B  IPP0  IPP2N  IPP3N  IPP4R  IPP4W  IPP5B
      {"Default", {60,    50,   55,    145,   145,   362,    3,    3,     3,     3,     3,    48}},
    };

    /***********************************************
    *                Organization
    ***********************************************/
    const int m_internal_prefetch_size = 16;

    inline static constexpr ImplDef m_levels = {
      "channel", "rank", "bankgroup", "bank", "row", "column",    
    };

    /***********************************************
    *             Requests & Commands
    ***********************************************/
    inline static constexpr ImplDef m_commands = {
      "ACT",
      "PRE",    "PREsb",
      "PRERD",  "PRERDsb",
      "RD",     "WR",     "RDA",     "WRA"
    };

    inline static const ImplLUT m_command_scopes = LUT (
      m_commands, m_levels, {
        {"ACT",     "row"},
        {"PRE",    "bank"}, {"PREsb",      "bank"},
        {"PRERD",  "bank"}, {"PRERDsb",    "bank"},
        {"RD",   "column"}, {"WR",       "column"}, {"RDA", "column"}, {"WRA", "column"}
      }
    );

    inline static const ImplLUT m_command_meta = LUT<DRAMCommandMeta> (
      m_commands, {
        //               open?  close?  access?  refresh?  samebank?
        {"ACT",         {true,  false,  false,   false,    false}},
        {"PRE",         {false, true,   false,   false,    false}},
        {"PREsb",       {false, true,   false,   false,    true }},
        {"PRERD",       {false, true,   false,   false,    false}},
        {"PRERDsb",     {false, true,   false,   false,    true }},
        {"RD",          {false, false,  true,    false,    false}},
        {"WR",          {false, false,  true,    false,    false}},
        {"RDA",         {false, true,   true,    false,    false}},
        {"WRA",         {false, true,   true,    false,    false}}
      }
    );

    inline static constexpr ImplDef m_requests = {
      "read",     "write", 
      "open-row", "close-row", "close-ro-row"
    };

    inline static const ImplLUT m_request_translations = LUT (
      m_requests, m_commands, {
        {"read",      "RD"}, {"write",      "WR"}, 
        {"open-row", "ACT"}, {"close-row", "PRE"}, {"close-ro-row", "PRERD"}
      }
    );

    /***********************************************
    *                   Timing
    ***********************************************/
    inline static constexpr ImplDef m_timings = {
      "rate", 
      "nBL", "nCL", "nRCD", "nRP", "nRPRD", "nRAS", "nRC", "nWR", "nRTP", "nCWL",
      "nPPD",
      "nCCDS", "nCCDS_WR", "nCCDS_WTR",
      "nCCDL", "nCCDL_WR", "nCCDL_WTR",
      "nRRDS", "nRRDL",
      "nFAW",
      "nCS",
      "tCK_ps"
    };
   
    /***********************************************
    *                   Power
    ***********************************************/
    inline static constexpr ImplDef m_voltages = {
      "VDD", "VPP"
    };
    
    inline static constexpr ImplDef m_currents = {
      "IDD0", "IDD2N", "IDD3N", "IDD4R", "IDD4W", "IDD5B",
      "IPP0", "IPP2N", "IPP3N", "IPP4R", "IPP4W", "IPP5B"
    };

    inline static constexpr ImplDef m_cmds_counted = {
      "ACT", "PRE", "PRERD", "RD", "WR",
    };

    /***********************************************
    *                 Node States
    ***********************************************/
    //[TODO] I want to get rid of the "Refreshing" state but need to edit power lambdas first
    inline static constexpr ImplDef m_states = {
      "Opened", "Closed", "PowerUp", "N/A", "Dirty", "Refreshing"
    };

    inline static const ImplLUT m_init_states = LUT (
      m_levels, m_states, {
        {"channel",   "N/A"    }, 
        {"rank",      "PowerUp"},
        {"bankgroup", "N/A"    },
        {"bank",      "Closed" },
        {"row",       "Closed" },
        {"column",    "N/A"    },
      }
    );

  public:
    struct Node : public DRAMNodeBase<URAM5> {
      Node(URAM5* dram, Node* parent, int level, int id) : DRAMNodeBase<URAM5>(dram, parent, level, id) {};
    };

    std::vector<Node*> m_channels;
    
    FuncMatrix<ActionFunc_t<Node>>  m_actions;
    FuncMatrix<PreqFunc_t<Node>>    m_preqs;
    FuncMatrix<RowhitFunc_t<Node>>  m_rowhits;
    FuncMatrix<RowopenFunc_t<Node>> m_rowopens;
    FuncMatrix<PowerFunc_t<Node>>   m_powers;

    double s_total_pre_energy = 0.0;
    double s_total_prerd_energy = 0.0;

  public:
    void tick() override {
      m_clk++;

      // Check if there is any future action at this cycle
      for (int i = m_future_actions.size() - 1; i >= 0; i--) {
        auto& future_action = m_future_actions[i];
        if (future_action.clk == m_clk) {
          handle_future_action(future_action.cmd, future_action.addr_vec);
          m_future_actions.erase(m_future_actions.begin() + i);
        }
      }
    };

    void init() override {
      RAMULATOR_DECLARE_SPECS();
      set_organization();
      set_timing_vals();

      set_actions();
      set_preqs();
      set_rowhits();
      set_rowopens();
      set_powers();
      
      create_nodes();
    };

    void issue_command(int command, const AddrVec_t& addr_vec) override {
      int channel_id = addr_vec[m_levels["channel"]];
      m_channels[channel_id]->update_timing(command, addr_vec, m_clk);
      m_channels[channel_id]->update_powers(command, addr_vec, m_clk);
      m_channels[channel_id]->update_states(command, addr_vec, m_clk);
    
      // Check if the command requires future action
      check_future_action(command, addr_vec);
    };

    void check_future_action(int command, const AddrVec_t& addr_vec) {
      switch (command) {
        default:
          break;
      }
    }

    void handle_future_action(int command, const AddrVec_t& addr_vec) {
      int channel_id = addr_vec[m_levels["channel"]];
      switch (command) {
        default:
          break;
      }
    };

    int get_preq_command(int command, const AddrVec_t& addr_vec) override {
      int channel_id = addr_vec[m_levels["channel"]];
      return m_channels[channel_id]->get_preq_command(command, addr_vec, m_clk);
    };

    bool check_ready(int command, const AddrVec_t& addr_vec) override {
      int channel_id = addr_vec[m_levels["channel"]];
      return m_channels[channel_id]->check_ready(command, addr_vec, m_clk);
    };

    bool check_rowbuffer_hit(int command, const AddrVec_t& addr_vec) override {
      int channel_id = addr_vec[m_levels["channel"]];
      return m_channels[channel_id]->check_rowbuffer_hit(command, addr_vec, m_clk);
    };
    
    bool check_node_open(int command, const AddrVec_t& addr_vec) override {
      int channel_id = addr_vec[m_levels["channel"]];
      return m_channels[channel_id]->check_node_open(command, addr_vec, m_clk);
    };

  private:
    void set_organization() {
      // Channel width
      m_channel_width = param_group("org").param<int>("channel_width").default_val(32);

      // Organization
      m_organization.count.resize(m_levels.size(), -1);

      // Load organization preset if provided
      if (auto preset_name = param_group("org").param<std::string>("preset").optional()) {
        if (org_presets.count(*preset_name) > 0) {
          m_organization = org_presets.at(*preset_name);
        } else {
          throw ConfigurationError("Unrecognized organization preset \"{}\" in {}!", *preset_name, get_name());
        }
      }

      // Override the preset with any provided settings
      if (auto dq = param_group("org").param<int>("dq").optional()) {
        m_organization.dq = *dq;
      }

      for (int i = 0; i < m_levels.size(); i++){
        auto level_name = m_levels(i);
        if (auto sz = param_group("org").param<int>(level_name).optional()) {
          m_organization.count[i] = *sz;
        }
      }

      if (auto density = param_group("org").param<int>("density").optional()) {
        m_organization.density = *density;
      }

      // Sanity check: is the calculated chip density the same as the provided one?
      size_t _density = size_t(m_organization.count[m_levels["bankgroup"]]) *
                        size_t(m_organization.count[m_levels["bank"]]) *
                        size_t(m_organization.count[m_levels["row"]]) *
                        size_t(m_organization.count[m_levels["column"]]) *
                        size_t(m_organization.dq);
      _density >>= 20;
      if (m_organization.density != _density) {
        throw ConfigurationError(
            "Calculated {} chip density {} Mb does not equal the provided density {} Mb!", 
            get_name(),
            _density, 
            m_organization.density
        );
      }
    };

    void set_timing_vals() {
      m_timing_vals.resize(m_timings.size(), -1);

      // Load timing preset if provided
      bool preset_provided = false;
      if (auto preset_name = param_group("timing").param<std::string>("preset").optional()) {
        if (timing_presets.count(*preset_name) > 0) {
          m_timing_vals = timing_presets.at(*preset_name);
          preset_provided = true;
        } else {
          throw ConfigurationError("Unrecognized timing preset \"{}\" in {}!", *preset_name, get_name());
        }
      }

      // Check for rate (in MT/s), and if provided, calculate and set tCK (in picosecond)
      if (auto dq = param_group("timing").param<int>("rate").optional()) {
        if (preset_provided) {
          throw ConfigurationError("Cannot change the transfer rate of {} when using a speed preset!", get_name());
        }
        m_timing_vals("rate") = *dq;
      }
      int tCK_ps = 1E6 / (m_timing_vals("rate") / 2);
      m_timing_vals("tCK_ps") = tCK_ps;

      // Load the organization specific timings
      int dq_id = [](int dq) -> int {
        switch (dq) {
          case 4:  return 0;
          case 8:  return 1;
          case 16: return 2;
          default: return -1;
        }
      }(m_organization.dq);

      int rate_id = [](int rate) -> int {
        switch (rate) {
          case 3200:  return 0;
          case 8800:  return 1;
          default:    return -1;
        }
      }(m_timing_vals("rate"));

      constexpr int nRRDL_TABLE[3][2] = {
      // 3200, 8800
        {5,    18}, // x4
        {5,    18}, // x8
        {5,    18}, // x16
      };
      constexpr int nFAW_TABLE[3][2] = {
      // 3200, 8800  
        {40,   33}, // x4
        {32,   33}, // x8
        {32,   41}, // x16
      };

      if (dq_id != -1 && rate_id != -1) {
        m_timing_vals("nRRDL") = nRRDL_TABLE[dq_id][rate_id];
        m_timing_vals("nFAW")  = nFAW_TABLE [dq_id][rate_id];
      }

      // tCCD_L_WR2 (with RMW) table
      constexpr int nCCD_L_WR2_TABLE[2] = {
      // 3200, 8800 
        32,    45
      };
      if (dq_id == 0) {
        m_timing_vals("nCCDL_WR") = nCCD_L_WR2_TABLE[rate_id];
      }

      // Overwrite timing parameters with any user-provided value
      // Rate and tCK should not be overwritten
      for (int i = 1; i < m_timings.size() - 1; i++) {
        auto timing_name = std::string(m_timings(i));

        if (auto provided_timing = param_group("timing").param<int>(timing_name).optional()) {
          // Check if the user specifies in the number of cycles (e.g., nRCD)
          m_timing_vals(i) = *provided_timing;
        } else if (auto provided_timing = param_group("timing").param<float>(timing_name.replace(0, 1, "t")).optional()) {
          // Check if the user specifies in nanoseconds (e.g., tRCD)
          m_timing_vals(i) = JEDEC_rounding_DDR5(*provided_timing, tCK_ps);
        }
      }

      // Scale timing parameters with any user-provided constants
      // Rate and tCK should not be overwritten
      for (int i = 1; i < m_timings.size() - 1; i++) {
        auto timing_name = std::string(m_timings(i)).replace(0, 1, "t");
        if (auto provided_timing = param_group("timing_scaling_factors").param<float>(timing_name).optional()) {
          m_timing_vals(i) = *provided_timing * m_timing_vals(i);
        }
      }
      m_timing_vals(m_timings["nRAS"]) = m_timing_vals(m_timings["nRCD"]);

      // Check if there is any uninitialized timings
      for (int i = 0; i < m_timing_vals.size(); i++) {
        if (m_timing_vals(i) == -1) {
          throw ConfigurationError("In \"{}\", timing {} is not specified!", get_name(), m_timings(i));
        }
      }      

      // Set read latency
      m_read_latency = m_timing_vals("nCL") + m_timing_vals("nBL");

      // Populate the timing constraints
      #define V(timing) (m_timing_vals(timing))
      auto all_commands = std::vector<std::string_view>(m_commands.begin(), m_commands.end());
      populate_timingcons(this, {
          /*** Channel ***/ 
          // Two-Cycle Commands
          {.level = "channel", .preceding = {"ACT", "RD", "RDA", "WR", "WRA"}, .following = all_commands, .latency = 2},

          // CAS <-> CAS
          /// Data bus occupancy
          {.level = "channel", .preceding = {"RD", "RDA"}, .following = {"RD", "RDA"}, .latency = V("nBL")},
          {.level = "channel", .preceding = {"WR", "WRA"}, .following = {"WR", "WRA"}, .latency = V("nBL")},

          /*** Rank (or different BankGroup) ***/ 
          // CAS <-> CAS
          /// nCCDS is the minimal latency for column commands 
          {.level = "rank", .preceding = {"RD", "RDA"}, .following = {"RD", "RDA"}, .latency = V("nCCDS")},
          {.level = "rank", .preceding = {"WR", "WRA"}, .following = {"WR", "WRA"}, .latency = V("nCCDS_WR")},
          /// RD <-> WR, Minimum Read to Write, Assuming Read DQS Offset = 0, tRPST = 0.5, tWPRE = 2 tCK                          
          {.level = "rank", .preceding = {"RD", "RDA"}, .following = {"WR", "WRA"}, .latency = V("nCL") + V("nBL") + 2 - V("nCWL") + 2},   // nCCDS_RTW
          /// WR <-> RD, Minimum Read after Write
          {.level = "rank", .preceding = {"WR", "WRA"}, .following = {"RD", "RDA"}, .latency = V("nCCDS_WTR")},
          /// CAS <-> CAS between sibling ranks, nCS (rank switching) is needed for new DQS
          {.level = "rank", .preceding = {"RD", "RDA"}, .following = {"RD", "RDA", "WR", "WRA"}, .latency = V("nBL") + V("nCS"), .is_sibling = true},
          {.level = "rank", .preceding = {"WR", "WRA"}, .following = {"RD", "RDA"}, .latency = V("nCL")  + V("nBL") + V("nCS") - V("nCWL"), .is_sibling = true},
          /// RAS <-> RAS
          {.level = "rank", .preceding = {"ACT"},    .following = {"ACT"},   .latency = V("nRRDS")},          
          {.level = "rank", .preceding = {"ACT"},    .following = {"ACT"},   .latency = V("nFAW"), .window = 4},          
          /*** Same Bank Group ***/ 
          /// CAS <-> CAS
          {.level = "bankgroup", .preceding = {"RD", "RDA"}, .following = {"RD", "RDA"}, .latency = V("nCCDL")},          
          {.level = "bankgroup", .preceding = {"WR", "WRA"}, .following = {"WR", "WRA"}, .latency = V("nCCDL_WR")},          
          {.level = "bankgroup", .preceding = {"WR", "WRA"}, .following = {"RD", "RDA"}, .latency = V("nCCDL_WTR")},
          /// RAS <-> RAS
          {.level = "bankgroup", .preceding = {"ACT"}, .following = {"ACT"}, .latency = V("nRRDL")},  

          /*** Bank ***/ 
          //TODO: if the below lines means 'following' is being sent directly after 'preceding', we can be sure that no WR commands are being sent after ACT
          {.level = "bank", .preceding = {"ACT"}, .following = {"ACT"}, .latency = V("nRC")},
          // {.level = "bank", .preceding = {"ACT"}, .following = {"ACT"}, .latency = V("nRAS") + V("nRPRD")},
          {.level = "bank", .preceding = {"ACT"}, .following = {"RD", "RDA", "WR", "WRA"}, .latency = V("nRCD")},
          {.level = "bank", .preceding = {"ACT"}, .following = {"PRE", "PREsb"}, .latency = V("nRAS")},
          {.level = "bank", .preceding = {"ACT"}, .following = {"PRERD", "PRERDsb"}, .latency = V("nRAS")},
          {.level = "bank", .preceding = {"PRE", "PREsb"}, .following = {"ACT"}, .latency = V("nRP")},
          {.level = "bank", .preceding = {"PRERD", "PRERDsb"}, .following = {"ACT"}, .latency = V("nRPRD")},
          {.level = "bank", .preceding = {"RD"},  .following = {"PRE", "PREsb"}, .latency = V("nRTP")},
          {.level = "bank", .preceding = {"RD"},  .following = {"PRERD", "PRERDsb"}, .latency = V("nRTP")},
          {.level = "bank", .preceding = {"WR"},  .following = {"PRE", "PREsb"}, .latency = V("nCWL") + V("nBL") + V("nWR")},  
          {.level = "bank", .preceding = {"WR"},  .following = {"PRERD", "PRERDsb"}, .latency = V("nCWL") + V("nBL") + V("nWR")},
          {.level = "bank", .preceding = {"RDA"}, .following = {"ACT"}, .latency = V("nRTP") + V("nRP")},
          {.level = "bank", .preceding = {"WRA"}, .following = {"ACT"}, .latency = V("nCWL") + V("nBL") + V("nWR") + V("nRP")},
          {.level = "bank", .preceding = {"WR"},  .following = {"RDA"}, .latency = V("nCWL") + V("nBL") + V("nWR") - V("nRTP")},
        }
      );
      #undef V

    };

    void set_actions() {
      m_actions.resize(m_levels.size(), std::vector<ActionFunc_t<Node>>(m_commands.size()));

      // Same-Bank Actions.
      m_actions[m_levels["bankgroup"]][m_commands["PREsb"]]   = Lambdas::Action::BankGroup::PREsb<URAM5>;
      m_actions[m_levels["bankgroup"]][m_commands["PRERDsb"]] = Lambdas::Action::BankGroup::PREsb<URAM5>;

      // Bank actions
      m_actions[m_levels["bank"]][m_commands["ACT"]]   = Lambdas::Action::Bank::ACT<URAM5>;
      m_actions[m_levels["bank"]][m_commands["PRE"]]   = Lambdas::Action::Bank::PRE<URAM5>;
      m_actions[m_levels["bank"]][m_commands["PRERD"]] = Lambdas::Action::Bank::PRE<URAM5>;
      m_actions[m_levels["bank"]][m_commands["RDA"]]   = Lambdas::Action::Bank::PRE<URAM5>;
      m_actions[m_levels["bank"]][m_commands["WRA"]]   = Lambdas::Action::Bank::PRE<URAM5>;

      m_actions[m_levels["bank"]][m_commands["WR"]] = [] (Node* node, int cmd, int target_id, Clk_t clk) {
        node->m_row_state[target_id] = m_states["Dirty"];
      };
    };

    void set_preqs() {
      m_preqs.resize(m_levels.size(), std::vector<PreqFunc_t<Node>>(m_commands.size()));

      auto RequireRowOpen = [](typename URAM5::Node* node, int cmd, const AddrVec_t& addr_vec, Clk_t clk) {
        switch (node->m_state) {
          case URAM5::m_states["Closed"]: return URAM5::m_commands["ACT"];
          case URAM5::m_states["Opened"]: {
            if (node->m_row_state.find(addr_vec[URAM5::m_levels["row"]]) != node->m_row_state.end()) {
              return cmd;
            } else {
              for (const auto& [row, state] : node->m_row_state) {
                if(state == m_states["Dirty"]) {
                  return URAM5::m_commands["PRE"];
                }
              }
              return URAM5::m_commands["PRERD"];
            }
          }    
          default: {
            spdlog::error("[Preq::Bank] Invalid bank state for an RD/WR command!");
            std::exit(-1);      
          } 
        }
      };

      auto RequireBankClosed = [](typename URAM5::Node* node, int cmd, const AddrVec_t& addr_vec, Clk_t clk) {
        switch (node->m_state) {
          case URAM5::m_states["Closed"]: return cmd;
          case URAM5::m_states["Opened"]: {
            for (const auto& [row, state] : node->m_row_state) {
              if(state == m_states["Dirty"]) {
                return m_commands["PRE"];
              }
            }
            return URAM5::m_commands["PRERD"];
          }
          default: {
            spdlog::error("[Preq::Bank] Invalid bank state for an RD/WR command!");
            std::exit(-1);      
          } 
        }
      };

      // Bank Preqs
      m_preqs[m_levels["bank"]][m_commands["RD"]]    = RequireRowOpen;
      m_preqs[m_levels["bank"]][m_commands["WR"]]    = RequireRowOpen;
      m_preqs[m_levels["bank"]][m_commands["ACT"]]   = RequireRowOpen;
      m_preqs[m_levels["bank"]][m_commands["PRE"]]   = RequireBankClosed;
      m_preqs[m_levels["bank"]][m_commands["PRERD"]] = RequireBankClosed;
    };

    void set_rowhits() {
      m_rowhits.resize(m_levels.size(), std::vector<RowhitFunc_t<Node>>(m_commands.size()));

      auto RDWR = [](typename URAM5::Node* node, int cmd, int target_id, Clk_t clk) {
        switch (node->m_state)  {
          case URAM5::m_states["Closed"]: return false;
          case URAM5::m_states["Opened"]:
            if (node->m_row_state.find(target_id) != node->m_row_state.end()) {
              return true;
            }
            else {
              return false;
            }
          default: {
            spdlog::error("[RowHit::Bank] Invalid bank state for an RD/WR command!");
            std::exit(-1);      
          }
        }
      };

      m_rowhits[m_levels["bank"]][m_commands["RD"]] = RDWR;
      m_rowhits[m_levels["bank"]][m_commands["WR"]] = RDWR;
    }


    void set_rowopens() {
      m_rowopens.resize(m_levels.size(), std::vector<RowhitFunc_t<Node>>(m_commands.size()));

      auto RDWR = [](typename URAM5::Node* node, int cmd, int target_id, Clk_t clk) {
        switch (node->m_state)  {
          case URAM5::m_states["Closed"]: return false;
          case URAM5::m_states["Opened"]: return true;
          default: {
            spdlog::error("[RowHit::Bank] Invalid bank state for an RD/WR command!");
            std::exit(-1);      
          }
        }
      };

      m_rowopens[m_levels["bank"]][m_commands["RD"]] = RDWR;
      m_rowopens[m_levels["bank"]][m_commands["WR"]] = RDWR;
    }

    void set_powers() {
      m_drampower_enable = param<bool>("drampower_enable").default_val(false);

      if (!m_drampower_enable)
        return;

      m_voltage_vals.resize(m_voltages.size(), -1);

      if (auto preset_name = param_group("voltage").param<std::string>("preset").optional()) {
        if (voltage_presets.count(*preset_name) > 0) {
          m_voltage_vals = voltage_presets.at(*preset_name);
        } else {
          throw ConfigurationError("Unrecognized voltage preset \"{}\" in {}!", *preset_name, get_name());
        }
      }

      m_current_vals.resize(m_currents.size(), -1);

      if (auto preset_name = param_group("current").param<std::string>("preset").optional()) {
        if (current_presets.count(*preset_name) > 0) {
          m_current_vals = current_presets.at(*preset_name);
        } else {
          throw ConfigurationError("Unrecognized current preset \"{}\" in {}!", *preset_name, get_name());
        }
      }

      for (int i = 0; i < m_voltages.size(); i++) {
        auto voltage_val = std::string(m_voltages(i));
        if (auto provided_voltage = param_group("voltage_scaling_factors").param<double>(voltage_val).optional()) {
          m_voltage_vals(i) = *provided_voltage * m_voltage_vals(i);
        }
      }

      for (int i = 0; i < m_currents.size(); i++) {
        auto current_val = std::string(m_currents(i));
        if (auto provided_current = param_group("current_scaling_factors").param<double>(current_val).optional()) {
          m_current_vals(i) = *provided_current * m_current_vals(i);
        }
      }

      m_power_debug = param<bool>("power_debug").default_val(false);

      // TODO: Check for multichannel configs.
      int num_channels = m_organization.count[m_levels["channel"]];
      int num_ranks = m_organization.count[m_levels["rank"]];
      m_power_stats.resize(num_channels * num_ranks);
      for (int i = 0; i < num_channels; i++) {
        for (int j = 0; j < num_ranks; j++) {
          m_power_stats[i * num_ranks + j].rank_id = i * num_ranks + j;
          m_power_stats[i * num_ranks + j].cmd_counters.resize(m_cmds_counted.size(), 0);
        }
      }

      m_powers.resize(m_levels.size(), std::vector<PowerFunc_t<Node>>(m_commands.size()));

      m_powers[m_levels["bank"]][m_commands["ACT"]]   = Lambdas::Power::Bank::ACT<URAM5>;
      m_powers[m_levels["bank"]][m_commands["PRE"]]   = Lambdas::Power::Bank::PRE<URAM5>;
      m_powers[m_levels["bank"]][m_commands["PRERD"]] = Lambdas::Power::Bank::PRERD<URAM5>;
      m_powers[m_levels["bank"]][m_commands["RD"]]    = Lambdas::Power::Bank::RD<URAM5>;
      m_powers[m_levels["bank"]][m_commands["WR"]]    = Lambdas::Power::Bank::WR<URAM5>;

      m_powers[m_levels["rank"]][m_commands["ACT"]]   = Lambdas::Power::Rank::ACT<URAM5>;
      m_powers[m_levels["rank"]][m_commands["PRE"]]   = Lambdas::Power::Rank::PRE<URAM5>;
      m_powers[m_levels["rank"]][m_commands["PRERD"]] = Lambdas::Power::Rank::PRERD<URAM5>;

      m_powers[m_levels["rank"]][m_commands["PREsb"]]   = Lambdas::Power::Rank::PREsb<URAM5>;
      m_powers[m_levels["rank"]][m_commands["PRERDsb"]] = Lambdas::Power::Rank::PRERDsb<URAM5>;

      // register stats
      register_stat(s_total_background_energy).name("total_background_energy");
      register_stat(s_total_cmd_energy       ).name("total_cmd_energy");
      register_stat(s_total_energy           ).name("total_energy");
      register_stat(s_total_pre_energy       ).name("total_pre_energy");
      register_stat(s_total_prerd_energy     ).name("total_prerd_energy");

            
      for (auto& power_stat : m_power_stats){
        register_stat(power_stat.total_background_energy).name("total_background_energy_rank{}", power_stat.rank_id);
        register_stat(power_stat.total_cmd_energy       ).name("total_cmd_energy_rank{}",        power_stat.rank_id);
        register_stat(power_stat.total_energy           ).name("total_energy_rank{}",            power_stat.rank_id);
        register_stat(power_stat.act_background_energy  ).name("act_background_energy_rank{}",   power_stat.rank_id);
        register_stat(power_stat.pre_background_energy  ).name("pre_background_energy_rank{}",   power_stat.rank_id);
        register_stat(power_stat.active_cycles          ).name("active_cycles_rank{}",           power_stat.rank_id);
        register_stat(power_stat.idle_cycles            ).name("idle_cycles_rank{}",             power_stat.rank_id);
      }
    }

    void create_nodes() {
      int num_channels = m_organization.count[m_levels["channel"]];
      for (int i = 0; i < num_channels; i++) {
        Node* channel = new Node(this, nullptr, 0, i);
        m_channels.push_back(channel);
      }
    }
    
    void finalize() override {
      if (!m_drampower_enable)
        return;

      int num_channels = m_organization.count[m_levels["channel"]];
      int num_ranks = m_organization.count[m_levels["rank"]];
      for (int i = 0; i < num_channels; i++) {
        for (int j = 0; j < num_ranks; j++) {
          process_rank_energy(m_power_stats[i * num_ranks + j], m_channels[i]->m_child_nodes[j]);
        }
      }
    }

    void process_rank_energy(PowerStats& rank_stats, Node* rank_node) {
      Lambdas::Power::Rank::finalize_rank<URAM5>(rank_node, 0, AddrVec_t(), m_clk);

      auto TS = [&](std::string_view timing)  { return m_timing_vals(timing);   };
      auto VE = [&](std::string_view voltage) { return m_voltage_vals(voltage); };
      auto CE = [&](std::string_view current) { return m_current_vals(current); };

      double tCK_ns = (double) TS("tCK_ps") / 1000.0;

      rank_stats.act_background_energy = (VE("VDD") * CE("IDD3N") + VE("VPP") * CE("IPP3N")) 
                                            * rank_stats.active_cycles * tCK_ns / 1E3;

      rank_stats.pre_background_energy = (VE("VDD") * CE("IDD2N") + VE("VPP") * CE("IPP2N")) 
                                            * rank_stats.idle_cycles * tCK_ns / 1E3;


      double act_cmd_energy    = (VE("VDD") * (CE("IDD0") - CE("IDD3N")) + VE("VPP") * (CE("IPP0") - CE("IPP3N"))) 
                                      * rank_stats.cmd_counters[m_cmds_counted("ACT")] * TS("nRAS") * tCK_ns / 1E3;

      double pre_cmd_energy    = (VE("VDD") * (CE("IDD0") - CE("IDD2N")) + VE("VPP") * (CE("IPP0") - CE("IPP2N"))) 
                                      * rank_stats.cmd_counters[m_cmds_counted("PRE")] * TS("nRP")  * tCK_ns / 1E3;

      double prerd_cmd_energy  = (VE("VDD") * (CE("IDD0") - CE("IDD2N")) + VE("VPP") * (CE("IPP0") - CE("IPP2N"))) 
                                      * rank_stats.cmd_counters[m_cmds_counted("PRERD")] * TS("nRPRD")  * tCK_ns / 1E3;

      double rd_cmd_energy     = (VE("VDD") * (CE("IDD4R") - CE("IDD3N")) + VE("VPP") * (CE("IPP4R") - CE("IPP3N"))) 
                                      * rank_stats.cmd_counters[m_cmds_counted("RD")] * TS("nBL") * tCK_ns / 1E3;

      double wr_cmd_energy     = (VE("VDD") * (CE("IDD4W") - CE("IDD3N")) + VE("VPP") * (CE("IPP4W") - CE("IPP3N"))) 
                                      * rank_stats.cmd_counters[m_cmds_counted("WR")] * TS("nBL") * tCK_ns / 1E3;


      rank_stats.total_background_energy = rank_stats.act_background_energy + rank_stats.pre_background_energy;
      rank_stats.total_cmd_energy = act_cmd_energy 
                                    + pre_cmd_energy
                                    + prerd_cmd_energy
                                    + rd_cmd_energy
                                    + wr_cmd_energy;

      rank_stats.total_energy = rank_stats.total_background_energy + rank_stats.total_cmd_energy;

      s_total_background_energy += rank_stats.total_background_energy;
      s_total_cmd_energy        += rank_stats.total_cmd_energy;
      s_total_energy            += rank_stats.total_energy;
      s_total_pre_energy        += pre_cmd_energy;
      s_total_prerd_energy      += prerd_cmd_energy;
    }
};

}        // namespace Ramulator
