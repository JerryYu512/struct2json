#include <vector>
#include <iostream>
#include "nlohmann/json.hpp"
#include "param_json2struct.h"
#include "param_struct2json.h"

using namespace nlohmann;
using namespace biot;

int main(void) {
	json j;
	j["bool"] = true;
	j["u1"] = 12;
	j["u2"] = -1;

	std::vector<int> a {
		1, 2,3,4
	};

	for (auto &item : a) {
		json t;
		t["k"] = item;
		j["list"].push_back(t);
	}

	std::cout << j.dump() << std::endl;

	AppCfgParamSet param;
	AppCfgParamSet param2;
	AppCfgParamSet param3(param);

	param = param2;
	// AppCfgParamProduct p;

	simdjson::dom::parser parser;
	simdjson::dom::element jj;
	auto error = parser.load("param.json").get(jj);

	json out;

	json2struct(jj, param);

	// p.uuid = "00";
	// param.product_l.push_back(p);
	// p.uuid = "--";
	// param.product_l.push_back(p);
	// p.uuid = "++";
	// param.product_l.push_back(p);

	// std::cout << param.product_l[0].uuid << std::endl;

	struct2json(param, out);
	std::cout << out.dump(2) << std::endl;

	return 0;
}