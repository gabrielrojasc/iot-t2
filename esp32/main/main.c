#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "esp_bt.h"
#include "esp_gap_ble_api.h"
#include "esp_gatts_api.h"
#include "esp_bt_defs.h"
#include "esp_bt_main.h"
#include "esp_gatt_common_api.h"
#include "sdkconfig.h"

#define GATTS_TAG "GATTS_DEMO"

void app_main()
{
  esp_err_t ret;

  // Initialize NVS.
  ret = nvs_flash_init();
  if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND)
  {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
  }
  ESP_ERROR_CHECK(ret);

  esp_bt_controller_config_t bt_cfg = BT_CONTROLLER_INIT_CONFIG_DEFAULT();
  ret = esp_bt_controller_init(&bt_cfg);
  if (ret)
  {
    ESP_LOGE(GATTS_TAG, "%s initialize controller failed\n", __func__);
    return;
  }
  ret = esp_bt_controller_enable(ESP_BT_MODE_BTDM);
  if (ret)
  {
    ESP_LOGE(GATTS_TAG, "%s enable controller failed\n", __func__);
    return;
  }
  ret = esp_bluedroid_init();
  if (ret)
  {
    ESP_LOGE(GATTS_TAG, "%s init bluetooth failed\n", __func__);
    return;
  }
  ret = esp_bluedroid_enable();
  if (ret)
  {
    ESP_LOGE(GATTS_TAG, "%s enable bluetooth failed\n", __func__);
    return;
  }
}
