//
//  AppDelegate.m
//  Droidboard
//
//  Created by Jack Cook on 9/20/14.
//  Copyright (c) 2014 CosmicByte. All rights reserved.
//

#import "AppDelegate.h"

@interface AppDelegate ()

@property (weak) IBOutlet NSWindow *window;
@end

@implementation AppDelegate

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
    NSAlert *storyboardAlert = [[NSAlert alloc] init];
    [storyboardAlert addButtonWithTitle:@"OK"];
    storyboardAlert.messageText = @"Select your Storyboard";
    storyboardAlert.informativeText = @"Select the .storyboard file that will be used in the conversion to Android.";
    storyboardAlert.alertStyle = NSInformationalAlertStyle;
    [storyboardAlert runModal];
    
    
    __block NSString *storyboardPath = @"";
    NSOpenPanel *storyboardPanel = [NSOpenPanel openPanel];
    storyboardPanel.allowedFileTypes = @[@"storyboard"];
    
    [storyboardPanel beginWithCompletionHandler:^(NSInteger result) {
        if (result == NSFileHandlingPanelOKButton) {
            storyboardPath = [NSString stringWithFormat:@"%@", storyboardPanel.URLs.firstObject];
            storyboardPath = [[storyboardPath stringByReplacingOccurrencesOfString:@"file://" withString:@""] stringByReplacingOccurrencesOfString:@"%20" withString:@" "];
            
            NSAlert *androidAlert = [[NSAlert alloc] init];
            [androidAlert addButtonWithTitle:@"OK"];
            androidAlert.messageText = @"Select your Project";
            androidAlert.informativeText = @"Select a folder containing your currently blank Android project in which the new files will be created.";
            androidAlert.alertStyle = NSInformationalAlertStyle;
            [androidAlert runModal];
            
            
            __block NSString *androidPath = @"";
            NSOpenPanel *androidPanel = [NSOpenPanel openPanel];
            androidPanel.canChooseFiles = NO;
            androidPanel.canChooseDirectories = YES;
            
            [androidPanel beginWithCompletionHandler:^(NSInteger result) {
                if (result == NSFileHandlingPanelOKButton) {
                    androidPath = [[NSString stringWithFormat:@"%@", androidPanel.URLs.firstObject] stringByReplacingOccurrencesOfString:@"file://" withString:@""];
                    androidPath = [androidPath stringByReplacingOccurrencesOfString:@"file://" withString:@""];
                    
                    [self executePythonScript:storyboardPath androidPath:androidPath];
                } else {
                    [[NSApplication sharedApplication] terminate:nil];
                }
            }];
        } else {
            [[NSApplication sharedApplication] terminate:nil];
        }
    }];
}

- (void)executePythonScript:(NSString *)storyboardPath androidPath:(NSString *)androidPath {
    NSTask *task = [[NSTask alloc] init];
    task.launchPath = @"/Library/Frameworks/Python.framework/Versions/3.4/bin/python3";
    task.arguments = @[@"/Users/jackcook/Desktop/Droidboard/convert.py", storyboardPath, androidPath];
    task.terminationHandler = ^(NSTask *task) {
        NSLog(@"completed: %@", task);
    };
    [task launch];
    
    NSAlert *doneAlert = [[NSAlert alloc] init];
    [doneAlert addButtonWithTitle:@"OK"];
    doneAlert.messageText = @"Done";
    doneAlert.informativeText = @"Your app has successfully been converted to Android.";
    doneAlert.alertStyle = NSInformationalAlertStyle;
    [doneAlert runModal];
    
    [[NSApplication sharedApplication] terminate:nil];
}

- (void)applicationWillTerminate:(NSNotification *)aNotification {
    // Insert code here to tear down your application
}

@end
