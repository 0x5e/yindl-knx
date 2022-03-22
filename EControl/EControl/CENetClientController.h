//
//  CENetClientController.h
//  EControl
//
//  Created by 高森 on 2022/3/22.
//

#ifndef CENetClientController_h
#define CENetClientController_h

@import UIKit;

@interface CENetClientController: UIViewController

- (void)RConnectENet;
- (char)GetnwOrww;
- (char)GetSock;
- (void)Close;
- (void)Inval;
- (void)ConnectENet;
- (void)SetENetConnecticonStatus:(int)arg2;
- (void)InvalShow;
- (int)NetWork_LayerBuffNum:(char *)arg2 length:(int)arg3;
- (void)ReadStream;

- (char)Write_FC_USER_LOG:(char *)arg2 pass:(char *)arg3;
- (char)Read_FC_USER_LOG_ACK:(void *)arg2;

- (char)Write_FC_HEARTBEAT;
- (char)Read_FC_HEARTBEAT_ACK:(void *)arg2;

- (char)Write_FC_DATA_GET_TAG_ALLDATA;
- (char)Read_FC_DATA_RETURN_TAG_ALLDATA:(void *)arg2
- (char)Read_FC_DATA_UPDATA_TAG_DATA:(void *)arg2;

- (char)Write_FC_DATA_WRITE_TAG:(int)arg2 data:(double)arg3;
- (char)Read_FC_DATA_WRITE_TAG_ACK:(void *)arg2; // return 0x1


@end

#endif /* CENetClientController_h */
