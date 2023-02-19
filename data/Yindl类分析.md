# Yindl类分析

AppDelegate

## SDK
### TCP
AsyncSocket
AsyncReadPacket
AsyncWritePacket

### 协议
TCP_FILE_Sock 文件传输
  [self ConnectServer:*qword_100071af8 port:60001];
  [self Write_FC_FILE_UPDOWNLOADDATA:99 pawword:" "];
  [self Read_FC_FILE_UPDOWNLOADDATA_H:]
    '收到文件头\n文件类型:%d\n文件大小:%.f\nMD5:'
  
CENetClientController 主要业务逻辑+UI状态

YINDL_Network_Layer 协议层模型
ProjectXMLParser  配置读写

### Model
Project_NSObject
AIR_NSObject
BLIND_NSObject
LIGHT_NSObject
MENU_NSObject
NEWFAN_NSObject
UNDERFLOOR_NSObject


## UI

### 通用组件
ASValuePopUpView
ASValueTrackingSlider
CTopButton
IPAD_TopView
UIMaskView
UIView_BackgroundView
FlipsideViewController

### 首页
IPAD_HOMEViewController
IPAD_ViewController
ViewController

### 设置
IPAD_MAIN_SETTING_ViewController

### 窗帘
IPAD_MAIN_BLIND_ViewController
IPAD_Blind_Group_List_PopViewController
IPAD_BLIND_TableView
IPAD_BLIND_TableViewCell
UIButton_BlindButton
UIBLINDUISlider

### 新风
IPAD_MAIN_NEWFAN_ViewController
IPAD_NEWFAN_Group_List_PopViewController
IPAD_NEWFAN_TableViewCell
IPAD_NEWFAN_UIView

### 空调
IPAD_MAIN_AIR_ViewController
IPAD_Air_Group_List_PopViewController
IPAD_AIR_TableView
IPAD_AIR_TableViewCell

### 地暖
IPAD_MAIN_UNDERFLOOR_ViewController
IPAD_UNDERFLOOR_Group_List_PopViewController
IPAD_UNDERFLOOR_TableView
IPAD_UNDERFLOOR_TableViewCell

### 灯
IPAD_MAIN_LIGHT_ViewController
IPAD_Light_Group_List_PopViewController
IPAD_LIGHT_UITableView
IPAD_LIGHT_TableView
IPAD_LIGHT_TableViewCell
UIButton_LightButton
