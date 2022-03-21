//
//  main.m
//  EControl
//
//  Created by 高森 on 2022/3/21.
//

#import <UIKit/UIKit.h>
#import "AppDelegate.h"

#import <dlfcn.h>
#import <mach/mach.h>
#import <mach-o/loader.h>
#import <mach-o/dyld.h>

int main(int argc, char * argv[]) {
    NSString * appDelegateClassName;
    @autoreleasepool {
        // Setup code that might create autoreleased objects goes here.
//        appDelegateClassName = NSStringFromClass([AppDelegate class]);
        
        
        NSString * dylibName = @"libEControl";
        NSString * path = [[NSBundle mainBundle] pathForResource:dylibName ofType:@"dylib" inDirectory:@"Frameworks"];
        if (dlopen(path.UTF8String, RTLD_NOW) == NULL){
            NSLog(@"dlopen failed ，error %s", dlerror());
            return 0;
        };
        
        uint32_t dylib_count = _dyld_image_count();
        uint64_t slide = 0;
        for (int i = 0; i < dylib_count; i ++) {
            const char * name = _dyld_get_image_name(i);
            if ([[NSString stringWithUTF8String:name] isEqualToString:path]) {
                slide = _dyld_get_image_vmaddr_slide(i);
            }
        }
        assert(slide != 0);
        
        appDelegateClassName = @"AppDelegate";
    }
    return UIApplicationMain(argc, argv, nil, appDelegateClassName);
}
