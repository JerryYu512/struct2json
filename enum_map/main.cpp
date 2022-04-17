#include "enum_map.hpp"
#include "enum_map.h"
#include <stdio.h>

int main(void) {
	const char *str = get_enum_str(AppMode::APP_DEV_GW_MODE);
	std::string str2 = get_enum_as_str(AppMode::APP_DEV_GW_MODE);

	printf("%s\n", str);
	printf("%s\n", str2.c_str());

	printf("v = %u\n", get_enum_value<AppMode>(str));
	printf("v = %u\n", (uint8_t)get_enum_value<AppMode>(nullptr));
	printf("v = %u\n", get_enum_value<AppMode>(""));
	printf("in range = %s\n", AppMode_in_enum_range(APP_DEV_GW_MODE) ? "true" : "false");
	printf("in range = %s\n", AppMode_in_enum_range((AppMode)99) ? "true" : "false");

	return 0;
}