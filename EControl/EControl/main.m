//
//  main.m
//  EControl
//
//  Created by 高森 on 2022/3/21.
//

#import <UIKit/UIKit.h>
//#import "AppDelegate.h"

int main(int argc, char * argv[]) {
    NSString * appDelegateClassName;
    @autoreleasepool {
        // Setup code that might create autoreleased objects goes here.
//        appDelegateClassName = NSStringFromClass([AppDelegate class]);
        appDelegateClassName = @"AppDelegate";
    }
    return UIApplicationMain(argc, argv, nil, appDelegateClassName);
}
