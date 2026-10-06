#import <Cocoa/Cocoa.h>

@class PetController;

@interface PetPanel : NSPanel
@end

@implementation PetPanel
- (BOOL)canBecomeKeyWindow { return NO; }
- (BOOL)canBecomeMainWindow { return NO; }
@end

@interface PetView : NSView
@property(nonatomic, weak) PetController *controller;
- (void)showWalkDirection:(CGFloat)direction frameIndex:(NSInteger)frameIndex;
- (void)showActionFrame:(NSInteger)frameIndex;
- (void)showPauseTransitionFrame:(NSInteger)frameIndex;
- (void)showResumeTransitionFrame:(NSInteger)frameIndex;
- (void)showStumbleFrame:(NSInteger)frameIndex;
- (void)showStruggleFrame:(NSInteger)frameIndex;
- (void)showMeditateFrame:(NSInteger)frameIndex;
@end

@interface PetController : NSObject
- (void)beginDragging;
- (void)continueDragging;
- (void)finishDragging;
@end

@implementation PetView {
    NSImageView *_imageView;
    NSArray<NSImage *> *_rightFrames;
    NSArray<NSImage *> *_leftFrames;
    NSArray<NSImage *> *_actionFrames;
    NSArray<NSImage *> *_pauseTransitionFrames;
    NSArray<NSImage *> *_resumeTransitionFrames;
    NSArray<NSImage *> *_stumbleFrames;
    NSArray<NSImage *> *_struggleFrames;
    NSArray<NSImage *> *_meditateFrames;
    NSInteger _shownMode;
    NSInteger _shownIndex;
    CGFloat _shownDirection;
}

- (instancetype)initWithFrame:(NSRect)frameRect {
    self = [super initWithFrame:frameRect];
    if (self) {
        self.wantsLayer = YES;
        self.layer.backgroundColor = NSColor.clearColor.CGColor;
        _shownMode = -1;
        _shownIndex = -1;
        _shownDirection = 0;
        _rightFrames = [self loadWalkFramesForDirection:@"right"];
        _leftFrames = [self loadWalkFramesForDirection:@"left"];
        _actionFrames = [self loadActionFrames];
        _pauseTransitionFrames = [self loadPauseTransitionFrames];
        _resumeTransitionFrames = [self loadResumeTransitionFrames];
        _stumbleFrames = [self loadStumbleFrames];
        _struggleFrames = [self loadStruggleFrames];
        _meditateFrames = [self loadMeditateFrames];

        _imageView = [[NSImageView alloc] initWithFrame:self.bounds];
        _imageView.imageScaling = NSImageScaleProportionallyUpOrDown;
        _imageView.imageAlignment = NSImageAlignCenter;
        _imageView.wantsLayer = YES;
        [self addSubview:_imageView];
        [self showWalkDirection:1 frameIndex:0];
    }
    return self;
}

- (NSArray<NSImage *> *)loadWalkFramesForDirection:(NSString *)direction {
    NSMutableArray<NSImage *> *frames = [NSMutableArray arrayWithCapacity:4];
    for (NSInteger index = 1; index <= 4; index++) {
        NSString *name = [NSString stringWithFormat:@"walk-square-%@-%ld", direction, (long)index];
        NSURL *url = [NSBundle.mainBundle URLForResource:name withExtension:@"png"];
        NSImage *image = url ? [[NSImage alloc] initWithContentsOfURL:url] : nil;
        if (image) [frames addObject:image];
    }
    return frames;
}

- (NSArray<NSImage *> *)loadActionFrames {
    NSMutableArray<NSImage *> *frames = [NSMutableArray arrayWithCapacity:29];
    for (NSInteger index = 1; index <= 29; index++) {
        NSString *name = [NSString stringWithFormat:@"action-%02ld", (long)index];
        NSURL *url = [NSBundle.mainBundle URLForResource:name withExtension:@"png"];
        NSImage *image = url ? [[NSImage alloc] initWithContentsOfURL:url] : nil;
        if (image) [frames addObject:image];
    }
    return frames;
}

- (NSArray<NSImage *> *)loadStruggleFrames {
    NSMutableArray<NSImage *> *frames = [NSMutableArray arrayWithCapacity:4];
    for (NSInteger index = 1; index <= 4; index++) {
        NSString *name = [NSString stringWithFormat:@"struggle-%02ld", (long)index];
        NSURL *url = [NSBundle.mainBundle URLForResource:name withExtension:@"png"];
        NSImage *image = url ? [[NSImage alloc] initWithContentsOfURL:url] : nil;
        if (image) [frames addObject:image];
    }
    return frames;
}

- (NSArray<NSImage *> *)loadPauseTransitionFrames {
    NSMutableArray<NSImage *> *frames = [NSMutableArray arrayWithCapacity:10];
    for (NSInteger index = 1; index <= 10; index++) {
        NSString *name = [NSString stringWithFormat:@"pause-transition-%02ld", (long)index];
        NSURL *url = [NSBundle.mainBundle URLForResource:name withExtension:@"png"];
        NSImage *image = url ? [[NSImage alloc] initWithContentsOfURL:url] : nil;
        if (image) [frames addObject:image];
    }
    return frames;
}

- (NSArray<NSImage *> *)loadResumeTransitionFrames {
    NSMutableArray<NSImage *> *frames = [NSMutableArray arrayWithCapacity:8];
    for (NSInteger index = 1; index <= 8; index++) {
        NSString *name = [NSString stringWithFormat:@"resume-transition-%02ld", (long)index];
        NSURL *url = [NSBundle.mainBundle URLForResource:name withExtension:@"png"];
        NSImage *image = url ? [[NSImage alloc] initWithContentsOfURL:url] : nil;
        if (image) [frames addObject:image];
    }
    return frames;
}

- (NSArray<NSImage *> *)loadMeditateFrames {
    NSMutableArray<NSImage *> *frames = [NSMutableArray arrayWithCapacity:24];
    for (NSInteger index = 1; index <= 24; index++) {
        NSString *name = [NSString stringWithFormat:@"meditate-%02ld", (long)index];
        NSURL *url = [NSBundle.mainBundle URLForResource:name withExtension:@"png"];
        NSImage *image = url ? [[NSImage alloc] initWithContentsOfURL:url] : nil;
        if (image) [frames addObject:image];
    }
    return frames;
}

- (NSArray<NSImage *> *)loadStumbleFrames {
    NSMutableArray<NSImage *> *frames = [NSMutableArray arrayWithCapacity:5];
    for (NSInteger index = 1; index <= 5; index++) {
        NSString *name = [NSString stringWithFormat:@"stumble-%02ld", (long)index];
        NSURL *url = [NSBundle.mainBundle URLForResource:name withExtension:@"png"];
        NSImage *image = url ? [[NSImage alloc] initWithContentsOfURL:url] : nil;
        if (image) [frames addObject:image];
    }
    return frames;
}

- (void)layout {
    [super layout];
    _imageView.frame = self.bounds;
}

- (void)showWalkDirection:(CGFloat)direction frameIndex:(NSInteger)frameIndex {
    NSArray<NSImage *> *frames = direction < 0 ? _leftFrames : _rightFrames;
    if (frames.count == 0) return;
    NSInteger safeIndex = frameIndex % frames.count;
    CGFloat normalizedDirection = direction < 0 ? -1 : 1;
    if (_shownMode == 0 && _shownIndex == safeIndex && _shownDirection == normalizedDirection) return;
    _shownMode = 0;
    _shownIndex = safeIndex;
    _shownDirection = normalizedDirection;
    _imageView.image = frames[safeIndex];
}

- (void)showActionFrame:(NSInteger)frameIndex {
    if (_actionFrames.count == 0) return;
    NSInteger safeIndex = MAX(0, MIN(frameIndex, (NSInteger)_actionFrames.count - 1));
    if (_shownMode == 1 && _shownIndex == safeIndex) return;
    _shownMode = 1;
    _shownIndex = safeIndex;
    _shownDirection = 1;
    _imageView.image = _actionFrames[safeIndex];
}

- (void)showStruggleFrame:(NSInteger)frameIndex {
    if (_struggleFrames.count == 0) return;
    NSInteger safeIndex = MAX(0, MIN(frameIndex, (NSInteger)_struggleFrames.count - 1));
    if (_shownMode == 2 && _shownIndex == safeIndex) return;
    _shownMode = 2;
    _shownIndex = safeIndex;
    _shownDirection = 1;
    _imageView.image = _struggleFrames[safeIndex];
}

- (void)showPauseTransitionFrame:(NSInteger)frameIndex {
    if (_pauseTransitionFrames.count == 0) return;
    NSInteger safeIndex = MAX(0, MIN(frameIndex, (NSInteger)_pauseTransitionFrames.count - 1));
    if (_shownMode == 4 && _shownIndex == safeIndex) return;
    _shownMode = 4;
    _shownIndex = safeIndex;
    _shownDirection = 1;
    _imageView.image = _pauseTransitionFrames[safeIndex];
}

- (void)showResumeTransitionFrame:(NSInteger)frameIndex {
    if (_resumeTransitionFrames.count == 0) return;
    NSInteger safeIndex = MAX(0, MIN(frameIndex, (NSInteger)_resumeTransitionFrames.count - 1));
    if (_shownMode == 5 && _shownIndex == safeIndex) return;
    _shownMode = 5;
    _shownIndex = safeIndex;
    _shownDirection = 1;
    _imageView.image = _resumeTransitionFrames[safeIndex];
}

- (void)showStumbleFrame:(NSInteger)frameIndex {
    if (_stumbleFrames.count == 0) return;
    NSInteger safeIndex = MAX(0, MIN(frameIndex, (NSInteger)_stumbleFrames.count - 1));
    if (_shownMode == 6 && _shownIndex == safeIndex) return;
    _shownMode = 6;
    _shownIndex = safeIndex;
    _shownDirection = 1;
    _imageView.image = _stumbleFrames[safeIndex];
}

- (void)showMeditateFrame:(NSInteger)frameIndex {
    if (_meditateFrames.count == 0) return;
    NSInteger safeIndex = frameIndex % _meditateFrames.count;
    if (_shownMode == 3 && _shownIndex == safeIndex) return;
    _shownMode = 3;
    _shownIndex = safeIndex;
    _shownDirection = 1;
    _imageView.image = _meditateFrames[safeIndex];
}

- (void)mouseDown:(NSEvent *)event { [self.controller beginDragging]; }
- (void)mouseDragged:(NSEvent *)event { [self.controller continueDragging]; }
- (void)mouseUp:(NSEvent *)event { [self.controller finishDragging]; }
@end

typedef NS_ENUM(NSInteger, PetMotionMode) {
    PetMotionModeWalking = 0,
    PetMotionModeStaffSpin = 1,
    PetMotionModePausing = 2,
    PetMotionModeResuming = 3,
    PetMotionModeStumbling = 4,
};

static const CGFloat PetAspectRatio = 1.0;
static const CGFloat PetSizeSmall = 180;
static const CGFloat PetSizeMedium = 230;
static const CGFloat PetSizeLarge = 290;
static const CGFloat WalkingSpeedVerySlow = 10;
static const CGFloat WalkingSpeedSlow = 18;
static const CGFloat WalkingSpeedLeisurely = 28;
static const NSTimeInterval WalkFrameDuration = 0.22;
static const NSTimeInterval MeditateFrameDuration = 0.10;
static const NSInteger ActionFrameCount = 29;
static const NSInteger PauseTransitionFrameCount = 10;
static const NSInteger ResumeTransitionFrameCount = 8;
static const NSInteger StumbleFrameCount = 5;
static const NSTimeInterval ActionFrameDurations[] = {
    0.250, 0.070, 0.070, 0.085, 0.085, 0.230,
    0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072,
    0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072, 0.072,
    0.260,
    0.160, 0.085, 0.085, 0.085, 0.075, 0.120,
};
static const NSTimeInterval PauseTransitionFrameDurations[] = {
    0.250, 0.070, 0.070, 0.085, 0.085, 0.180, 0.180, 0.180, 0.220, 0.120,
};
static const NSTimeInterval ResumeTransitionFrameDurations[] = {
    0.100, 0.100, 0.120, 0.100, 0.100, 0.080, 0.080, 0.140,
};
static const NSTimeInterval StumbleFrameDurations[] = {
    0.100, 0.120, 0.220, 0.140, 0.180,
};
static const NSInteger StruggleStepCount = 6;
static const NSInteger StruggleFrameSequence[] = {0, 1, 2, 3, 2, 1};
static const NSTimeInterval StruggleFrameDurations[] = {
    0.190, 0.180, 0.160, 0.180, 0.160, 0.180,
};

@interface PetController ()
@property(nonatomic, strong) NSStatusItem *statusItem;
@property(nonatomic, strong) PetPanel *panel;
@property(nonatomic, strong) PetView *petView;
@property(nonatomic, strong) NSTimer *timer;
@property(nonatomic, strong) NSMenuItem *pauseItem;
@property(nonatomic, strong) NSMenuItem *visibilityItem;
@property(nonatomic, strong) NSMenuItem *walkingModeItem;
@property(nonatomic, strong) NSMenuItem *steppingModeItem;
@property(nonatomic, strong) NSScreen *activityScreen;
@property(nonatomic) NSTimeInterval lastUpdate;
@property(nonatomic) NSTimeInterval animationTime;
@property(nonatomic) NSTimeInterval actionElapsed;
@property(nonatomic) NSTimeInterval timeUntilAction;
@property(nonatomic) NSTimeInterval timeUntilStumble;
@property(nonatomic) NSInteger actionFrameIndex;
@property(nonatomic) NSInteger pauseTransitionFrameIndex;
@property(nonatomic) NSInteger resumeTransitionFrameIndex;
@property(nonatomic) NSInteger stumbleFrameIndex;
@property(nonatomic) NSInteger pauseStaffTargetIndex;
@property(nonatomic) NSInteger struggleStepIndex;
@property(nonatomic) NSTimeInterval struggleElapsed;
@property(nonatomic) NSTimeInterval meditationTime;
@property(nonatomic) NSTimeInterval pauseTransitionElapsed;
@property(nonatomic) NSTimeInterval resumeTransitionElapsed;
@property(nonatomic) NSTimeInterval stumbleElapsed;
@property(nonatomic) PetMotionMode motionMode;
@property(nonatomic) CGFloat direction;
@property(nonatomic) CGFloat petHeight;
@property(nonatomic) CGFloat walkingSpeed;
@property(nonatomic) CGFloat movementX;
@property(nonatomic) NSPoint dragOffset;
@property(nonatomic) BOOL dragging;
@property(nonatomic) BOOL paused;
@property(nonatomic) BOOL pauseRequested;
@property(nonatomic) BOOL hidden;
@property(nonatomic) BOOL movesAcrossScreen;
@end

@implementation PetController

- (instancetype)init {
    self = [super init];
    if (self) {
        _direction = 1;
        _motionMode = PetMotionModeWalking;
        _pauseStaffTargetIndex = -1;
        _timeUntilAction = 5.0;
        _timeUntilStumble = [self randomStumbleDelay];

        NSUserDefaults *defaults = NSUserDefaults.standardUserDefaults;
        _petHeight = [defaults objectForKey:@"walkOnlyPetSizeV1"]
            ? [defaults doubleForKey:@"walkOnlyPetSizeV1"] : PetSizeMedium;
        _walkingSpeed = [defaults objectForKey:@"walkingSpeedV2"]
            ? [defaults doubleForKey:@"walkingSpeedV2"] : WalkingSpeedSlow;
        _movesAcrossScreen = [defaults objectForKey:@"movesAcrossScreenV1"]
            ? [defaults boolForKey:@"movesAcrossScreenV1"] : YES;

        CGFloat width = _petHeight * PetAspectRatio;
        _panel = [[PetPanel alloc] initWithContentRect:NSMakeRect(80, 80, width, _petHeight)
                                            styleMask:NSWindowStyleMaskBorderless | NSWindowStyleMaskNonactivatingPanel
                                              backing:NSBackingStoreBuffered
                                                defer:NO];
        _panel.backgroundColor = NSColor.clearColor;
        _panel.opaque = NO;
        _panel.hasShadow = NO;
        _panel.level = NSFloatingWindowLevel;
        _panel.collectionBehavior = NSWindowCollectionBehaviorCanJoinAllSpaces |
                                    NSWindowCollectionBehaviorFullScreenAuxiliary |
                                    NSWindowCollectionBehaviorStationary;
        _panel.movable = NO;
        _panel.hidesOnDeactivate = NO;
        _panel.animationBehavior = NSWindowAnimationBehaviorNone;

        _petView = [[PetView alloc] initWithFrame:NSMakeRect(0, 0, width, _petHeight)];
        _petView.controller = self;
        _panel.contentView = _petView;

        [self configureStatusItem];
        NSNumber *savedX = [defaults objectForKey:@"walkOnlyLastXV1"];
        NSNumber *savedY = [defaults objectForKey:@"freePlacementLastYV1"];
        if (savedX && savedY) {
            [self placeNearX:savedX.doubleValue y:savedY.doubleValue];
        } else {
            [self placeOnGroundNearX:savedX ? savedX.doubleValue : NAN];
        }
        [_panel orderFrontRegardless];

        _lastUpdate = NSProcessInfo.processInfo.systemUptime;
        _timer = [NSTimer timerWithTimeInterval:(1.0 / 30.0)
                                        target:self
                                      selector:@selector(tick:)
                                      userInfo:nil
                                       repeats:YES];
        [NSRunLoop.mainRunLoop addTimer:_timer forMode:NSRunLoopCommonModes];
    }
    return self;
}

- (NSTimeInterval)randomActionDelay {
    return 11.0 + ((NSTimeInterval)arc4random_uniform(7001) / 1000.0);
}

- (NSTimeInterval)randomStumbleDelay {
    return 24.0 + ((NSTimeInterval)arc4random_uniform(24001) / 1000.0);
}

- (void)configureStatusItem {
    self.statusItem = [NSStatusBar.systemStatusBar statusItemWithLength:NSVariableStatusItemLength];
    NSURL *iconURL = [NSBundle.mainBundle URLForResource:@"status-icon" withExtension:@"png"];
    NSImage *statusIcon = iconURL ? [[NSImage alloc] initWithContentsOfURL:iconURL] : nil;
    if (statusIcon) {
        statusIcon.size = NSMakeSize(18, 18);
        statusIcon.template = YES;
    } else {
        statusIcon = [NSImage imageWithSystemSymbolName:@"person.crop.circle"
                              accessibilityDescription:@"艾丝蒂尔桌宠"];
    }
    self.statusItem.button.image = statusIcon;
    self.statusItem.button.toolTip = @"艾丝蒂尔桌宠";

    NSMenu *menu = [[NSMenu alloc] init];
    self.pauseItem = [[NSMenuItem alloc] initWithTitle:@"暂停" action:@selector(togglePause:) keyEquivalent:@"p"];
    self.pauseItem.target = self;
    [menu addItem:self.pauseItem];

    self.visibilityItem = [[NSMenuItem alloc] initWithTitle:@"隐藏艾丝蒂尔"
                                                    action:@selector(toggleVisibility:)
                                             keyEquivalent:@"h"];
    self.visibilityItem.target = self;
    [menu addItem:self.visibilityItem];
    [menu addItem:NSMenuItem.separatorItem];

    NSMenu *sizeMenu = [[NSMenu alloc] init];
    [self addChoiceToMenu:sizeMenu title:@"小" value:PetSizeSmall selected:self.petHeight action:@selector(changeSize:)];
    [self addChoiceToMenu:sizeMenu title:@"中" value:PetSizeMedium selected:self.petHeight action:@selector(changeSize:)];
    [self addChoiceToMenu:sizeMenu title:@"大" value:PetSizeLarge selected:self.petHeight action:@selector(changeSize:)];
    NSMenuItem *sizeRoot = [[NSMenuItem alloc] initWithTitle:@"大小" action:nil keyEquivalent:@""];
    sizeRoot.submenu = sizeMenu;
    [menu addItem:sizeRoot];

    NSMenu *movementMenu = [[NSMenu alloc] init];
    self.walkingModeItem = [[NSMenuItem alloc] initWithTitle:@"走路"
                                                     action:@selector(changeMovementMode:)
                                              keyEquivalent:@""];
    self.walkingModeItem.target = self;
    self.walkingModeItem.representedObject = @YES;
    self.walkingModeItem.state = self.movesAcrossScreen ? NSControlStateValueOn : NSControlStateValueOff;
    [movementMenu addItem:self.walkingModeItem];

    self.steppingModeItem = [[NSMenuItem alloc] initWithTitle:@"原地踏步"
                                                      action:@selector(changeMovementMode:)
                                               keyEquivalent:@""];
    self.steppingModeItem.target = self;
    self.steppingModeItem.representedObject = @NO;
    self.steppingModeItem.state = self.movesAcrossScreen ? NSControlStateValueOff : NSControlStateValueOn;
    [movementMenu addItem:self.steppingModeItem];

    NSMenuItem *movementRoot = [[NSMenuItem alloc] initWithTitle:@"移动方式" action:nil keyEquivalent:@""];
    movementRoot.submenu = movementMenu;
    [menu addItem:movementRoot];

    NSMenu *speedMenu = [[NSMenu alloc] init];
    [self addChoiceToMenu:speedMenu title:@"很慢" value:WalkingSpeedVerySlow selected:self.walkingSpeed action:@selector(changeSpeed:)];
    [self addChoiceToMenu:speedMenu title:@"慢（默认）" value:WalkingSpeedSlow selected:self.walkingSpeed action:@selector(changeSpeed:)];
    [self addChoiceToMenu:speedMenu title:@"悠闲" value:WalkingSpeedLeisurely selected:self.walkingSpeed action:@selector(changeSpeed:)];
    NSMenuItem *speedRoot = [[NSMenuItem alloc] initWithTitle:@"行走速度" action:nil keyEquivalent:@""];
    speedRoot.submenu = speedMenu;
    [menu addItem:speedRoot];

    NSMenuItem *returnItem = [[NSMenuItem alloc] initWithTitle:@"回到主屏幕底部"
                                                       action:@selector(returnToMainScreen:)
                                                keyEquivalent:@"r"];
    returnItem.target = self;
    [menu addItem:returnItem];
    [menu addItem:NSMenuItem.separatorItem];

    NSMenuItem *quitItem = [[NSMenuItem alloc] initWithTitle:@"退出" action:@selector(quit:) keyEquivalent:@"q"];
    quitItem.target = self;
    [menu addItem:quitItem];
    self.statusItem.menu = menu;
}

- (void)addChoiceToMenu:(NSMenu *)menu title:(NSString *)title value:(CGFloat)value
               selected:(CGFloat)selected action:(SEL)action {
    NSMenuItem *item = [[NSMenuItem alloc] initWithTitle:title action:action keyEquivalent:@""];
    item.target = self;
    item.representedObject = @(value);
    item.state = fabs(value - selected) < 0.1 ? NSControlStateValueOn : NSControlStateValueOff;
    [menu addItem:item];
}

- (NSScreen *)screenContainingPoint:(NSPoint)point {
    NSScreen *nearest = nil;
    CGFloat nearestDistance = CGFLOAT_MAX;
    for (NSScreen *screen in NSScreen.screens) {
        if (NSPointInRect(point, screen.frame)) return screen;
        NSRect frame = screen.frame;
        CGFloat nearestX = fmax(NSMinX(frame), fmin(point.x, NSMaxX(frame)));
        CGFloat nearestY = fmax(NSMinY(frame), fmin(point.y, NSMaxY(frame)));
        CGFloat dx = point.x - nearestX;
        CGFloat dy = point.y - nearestY;
        CGFloat distance = dx * dx + dy * dy;
        if (distance < nearestDistance) {
            nearestDistance = distance;
            nearest = screen;
        }
    }
    return nearest ?: NSScreen.mainScreen ?: NSScreen.screens.firstObject;
}

- (NSScreen *)screenForPanel {
    NSPoint center = NSMakePoint(NSMidX(self.panel.frame), NSMidY(self.panel.frame));
    return [self screenContainingPoint:center];
}

- (NSPoint)clampedOrigin:(NSPoint)origin onScreen:(NSScreen *)screen {
    NSRect visible = screen.visibleFrame;
    NSRect frame = self.panel.frame;
    origin.x = fmax(NSMinX(visible), fmin(origin.x, NSMaxX(visible) - NSWidth(frame)));
    origin.y = fmax(NSMinY(visible), fmin(origin.y, NSMaxY(visible) - NSHeight(frame)));
    return origin;
}

- (void)placeNearX:(CGFloat)x y:(CGFloat)y {
    CGFloat width = self.petHeight * PetAspectRatio;
    NSScreen *screen = [self screenContainingPoint:NSMakePoint(x + width / 2.0, y + self.petHeight / 2.0)];
    self.activityScreen = screen;
    [self.panel setFrame:NSMakeRect(x, y, width, self.petHeight) display:YES];
    [self.panel setFrameOrigin:[self clampedOrigin:self.panel.frame.origin onScreen:screen]];
    self.movementX = NSMinX(self.panel.frame);
    self.petView.frame = NSMakeRect(0, 0, width, self.petHeight);
}

- (void)placeOnGroundNearX:(CGFloat)x {
    NSScreen *screen = self.activityScreen ?: NSScreen.mainScreen ?: NSScreen.screens.firstObject;
    self.activityScreen = screen;
    NSRect visible = screen.visibleFrame;
    CGFloat resolvedX = isnan(x) ? NSMinX(visible) + 50 : x;
    [self placeNearX:resolvedX y:NSMinY(visible) + 2];
}

- (void)savePosition {
    NSPoint origin = self.panel.frame.origin;
    [NSUserDefaults.standardUserDefaults setDouble:origin.x forKey:@"walkOnlyLastXV1"];
    [NSUserDefaults.standardUserDefaults setDouble:origin.y forKey:@"freePlacementLastYV1"];
}

- (void)startStaffSpin {
    self.motionMode = PetMotionModeStaffSpin;
    self.actionFrameIndex = 0;
    self.actionElapsed = 0;
    [self.petView showActionFrame:0];
}

- (void)finishStaffSpin {
    self.motionMode = PetMotionModeWalking;
    self.direction = 1;
    self.animationTime = 3 * WalkFrameDuration;
    self.timeUntilAction = [self randomActionDelay];
    [self.petView showWalkDirection:1 frameIndex:3];
}

- (void)advanceStaffSpinBy:(NSTimeInterval)delta {
    self.actionElapsed += delta;
    while (self.actionFrameIndex < ActionFrameCount &&
           self.actionElapsed >= ActionFrameDurations[self.actionFrameIndex]) {
        self.actionElapsed -= ActionFrameDurations[self.actionFrameIndex];
        self.actionFrameIndex += 1;
    }
    if (self.actionFrameIndex >= ActionFrameCount) {
        [self finishStaffSpin];
        return;
    }
    if (self.pauseRequested && self.pauseStaffTargetIndex >= 0 &&
        self.actionFrameIndex >= self.pauseStaffTargetIndex) {
        [self startPauseTransitionAtIndex:6];
        return;
    }
    [self.petView showActionFrame:self.actionFrameIndex];
}

- (void)startPauseTransitionAtIndex:(NSInteger)frameIndex {
    self.motionMode = PetMotionModePausing;
    self.pauseTransitionFrameIndex = MAX(0, MIN(frameIndex, PauseTransitionFrameCount - 1));
    self.pauseTransitionElapsed = 0;
    self.pauseStaffTargetIndex = -1;
    [self.petView showPauseTransitionFrame:self.pauseTransitionFrameIndex];
}

- (void)finishPauseTransition {
    if (self.pauseRequested) {
        self.paused = YES;
        self.motionMode = PetMotionModeWalking;
        self.meditationTime = 0;
        [self.petView showMeditateFrame:0];
    } else {
        self.motionMode = PetMotionModeWalking;
        self.animationTime = 3 * WalkFrameDuration;
        self.timeUntilAction = [self randomActionDelay];
        [self.petView showWalkDirection:1 frameIndex:3];
    }
}

- (void)advancePauseTransitionBy:(NSTimeInterval)delta {
    self.pauseTransitionElapsed += delta;
    while (self.pauseTransitionFrameIndex < PauseTransitionFrameCount &&
           self.pauseTransitionElapsed >= PauseTransitionFrameDurations[self.pauseTransitionFrameIndex]) {
        self.pauseTransitionElapsed -= PauseTransitionFrameDurations[self.pauseTransitionFrameIndex];
        self.pauseTransitionFrameIndex += 1;
    }
    if (self.pauseTransitionFrameIndex >= PauseTransitionFrameCount) {
        [self finishPauseTransition];
        return;
    }
    [self.petView showPauseTransitionFrame:self.pauseTransitionFrameIndex];
}

- (void)startResumeTransition {
    self.paused = NO;
    self.pauseRequested = NO;
    self.pauseStaffTargetIndex = -1;
    self.motionMode = PetMotionModeResuming;
    self.resumeTransitionFrameIndex = 0;
    self.resumeTransitionElapsed = 0;
    [self.petView showResumeTransitionFrame:0];
}

- (void)finishResumeTransition {
    self.motionMode = PetMotionModeWalking;
    self.direction = 1;
    self.animationTime = 3 * WalkFrameDuration;
    self.timeUntilAction = [self randomActionDelay];
    [self.petView showWalkDirection:1 frameIndex:3];
}

- (void)advanceResumeTransitionBy:(NSTimeInterval)delta {
    self.resumeTransitionElapsed += delta;
    while (self.resumeTransitionFrameIndex < ResumeTransitionFrameCount &&
           self.resumeTransitionElapsed >= ResumeTransitionFrameDurations[self.resumeTransitionFrameIndex]) {
        self.resumeTransitionElapsed -= ResumeTransitionFrameDurations[self.resumeTransitionFrameIndex];
        self.resumeTransitionFrameIndex += 1;
    }
    if (self.resumeTransitionFrameIndex >= ResumeTransitionFrameCount) {
        [self finishResumeTransition];
        return;
    }
    [self.petView showResumeTransitionFrame:self.resumeTransitionFrameIndex];
}

- (void)startStumble {
    self.motionMode = PetMotionModeStumbling;
    self.stumbleFrameIndex = 0;
    self.stumbleElapsed = 0;
    [self.petView showStumbleFrame:0];
}

- (void)finishStumble {
    self.motionMode = PetMotionModeWalking;
    self.direction = 1;
    self.animationTime = 0;
    self.timeUntilStumble = [self randomStumbleDelay];
    [self.petView showWalkDirection:1 frameIndex:0];
}

- (void)advanceStumbleBy:(NSTimeInterval)delta {
    self.stumbleElapsed += delta;
    while (self.stumbleFrameIndex < StumbleFrameCount &&
           self.stumbleElapsed >= StumbleFrameDurations[self.stumbleFrameIndex]) {
        self.stumbleElapsed -= StumbleFrameDurations[self.stumbleFrameIndex];
        self.stumbleFrameIndex += 1;
    }
    if (self.stumbleFrameIndex >= StumbleFrameCount) {
        [self finishStumble];
        return;
    }
    [self.petView showStumbleFrame:self.stumbleFrameIndex];
}

- (void)advanceStruggleBy:(NSTimeInterval)delta {
    self.struggleElapsed += delta;
    while (self.struggleElapsed >= StruggleFrameDurations[self.struggleStepIndex]) {
        self.struggleElapsed -= StruggleFrameDurations[self.struggleStepIndex];
        self.struggleStepIndex = (self.struggleStepIndex + 1) % StruggleStepCount;
    }
    [self.petView showStruggleFrame:StruggleFrameSequence[self.struggleStepIndex]];
}

- (void)advancePauseAnimationBy:(NSTimeInterval)delta {
    self.meditationTime += delta;
    NSInteger frameIndex = (NSInteger)floor(self.meditationTime / MeditateFrameDuration) % 24;
    [self.petView showMeditateFrame:frameIndex];
}

- (void)tick:(NSTimer *)timer {
    NSTimeInterval now = NSProcessInfo.processInfo.systemUptime;
    NSTimeInterval delta = fmin(now - self.lastUpdate, 0.1);
    self.lastUpdate = now;
    if (self.hidden) return;

    if (self.dragging) {
        [self advanceStruggleBy:delta];
        return;
    }

    if (self.paused) {
        [self advancePauseAnimationBy:delta];
        return;
    }

    if (self.motionMode == PetMotionModePausing) {
        [self advancePauseTransitionBy:delta];
        return;
    }

    if (self.motionMode == PetMotionModeResuming) {
        [self advanceResumeTransitionBy:delta];
        return;
    }

    if (self.motionMode == PetMotionModeStaffSpin) {
        [self advanceStaffSpinBy:delta];
        return;
    }

    if (self.motionMode == PetMotionModeStumbling) {
        [self advanceStumbleBy:delta];
        return;
    }

    self.animationTime += delta;
    NSInteger frameIndex = (NSInteger)floor(self.animationTime / WalkFrameDuration) % 4;
    [self.petView showWalkDirection:self.direction frameIndex:frameIndex];
    if (self.pauseRequested && frameIndex == 3) {
        [self startPauseTransitionAtIndex:0];
        return;
    }
    self.timeUntilStumble -= delta;
    if (!self.pauseRequested && self.timeUntilStumble <= 0 && frameIndex == 0) {
        [self startStumble];
        return;
    }
    self.timeUntilAction -= delta;
    if (!self.pauseRequested && self.timeUntilAction <= 0) {
        if (self.direction < 0) {
            self.direction = 1;
            self.timeUntilAction = 0.75;
            [self.petView showWalkDirection:1 frameIndex:frameIndex];
        } else {
            self.animationTime = 3 * WalkFrameDuration;
            [self startStaffSpin];
            return;
        }
    }

    if (!self.movesAcrossScreen) return;

    NSScreen *screen = self.activityScreen ?: [self screenForPanel];
    if (!screen) return;
    self.activityScreen = screen;
    NSRect visible = screen.visibleFrame;
    NSRect frame = self.panel.frame;
    self.movementX += self.direction * self.walkingSpeed * delta;

    CGFloat leftEdge = NSMinX(visible);
    CGFloat rightEdge = NSMaxX(visible) - NSWidth(frame);
    if (self.movementX >= rightEdge) {
        self.movementX = leftEdge - NSWidth(frame);
        self.direction = 1;
        self.animationTime = 0;
        [self.petView showWalkDirection:1 frameIndex:0];
    }
    frame.origin.x = round(self.movementX);
    [self.panel setFrameOrigin:frame.origin];
}

- (void)beginDragging {
    self.dragging = YES;
    self.motionMode = PetMotionModeWalking;
    self.struggleStepIndex = 0;
    self.struggleElapsed = 0;
    self.timeUntilAction = [self randomActionDelay];
    self.timeUntilStumble = [self randomStumbleDelay];
    [self.petView showStruggleFrame:StruggleFrameSequence[0]];
    NSPoint mouse = NSEvent.mouseLocation;
    self.dragOffset = NSMakePoint(mouse.x - NSMinX(self.panel.frame), mouse.y - NSMinY(self.panel.frame));
}

- (void)continueDragging {
    if (!self.dragging) return;
    NSPoint mouse = NSEvent.mouseLocation;
    [self.panel setFrameOrigin:NSMakePoint(mouse.x - self.dragOffset.x, mouse.y - self.dragOffset.y)];
}

- (void)finishDragging {
    self.dragging = NO;
    NSScreen *screen = [self screenForPanel];
    if (!screen) return;
    self.activityScreen = screen;
    [self.panel setFrameOrigin:[self clampedOrigin:self.panel.frame.origin onScreen:screen]];
    self.movementX = NSMinX(self.panel.frame);
    [self savePosition];
    if (self.paused) {
        NSInteger frameIndex = (NSInteger)floor(self.meditationTime / MeditateFrameDuration) % 24;
        [self.petView showMeditateFrame:frameIndex];
    } else {
        NSInteger frameIndex = (NSInteger)floor(self.animationTime / WalkFrameDuration) % 4;
        [self.petView showWalkDirection:self.direction frameIndex:frameIndex];
    }
}

- (void)togglePause:(id)sender {
    if (self.paused) {
        self.pauseItem.title = @"暂停";
        [self startResumeTransition];
    } else if (self.pauseRequested) {
        self.pauseRequested = NO;
        self.pauseStaffTargetIndex = -1;
        self.pauseItem.title = @"暂停";
    } else {
        self.pauseRequested = YES;
        self.pauseItem.title = @"继续";
        if (self.motionMode == PetMotionModeStaffSpin) {
            if (self.actionFrameIndex <= 5) {
                self.pauseStaffTargetIndex = 5;
            } else if (self.actionFrameIndex <= 22) {
                self.pauseStaffTargetIndex = 22;
            } else {
                self.pauseStaffTargetIndex = -1;
            }
        } else if (self.motionMode == PetMotionModeWalking && !self.dragging) {
            NSInteger frameIndex = (NSInteger)floor(self.animationTime / WalkFrameDuration) % 4;
            if (frameIndex == 3) [self startPauseTransitionAtIndex:0];
        }
    }
    self.lastUpdate = NSProcessInfo.processInfo.systemUptime;
}

- (void)toggleVisibility:(id)sender {
    self.hidden = !self.hidden;
    if (self.hidden) {
        [self.panel orderOut:nil];
        self.visibilityItem.title = @"显示艾丝蒂尔";
    } else {
        [self.panel orderFrontRegardless];
        self.visibilityItem.title = @"隐藏艾丝蒂尔";
        self.lastUpdate = NSProcessInfo.processInfo.systemUptime;
    }
}

- (void)changeSize:(NSMenuItem *)sender {
    self.petHeight = [(NSNumber *)sender.representedObject doubleValue];
    [NSUserDefaults.standardUserDefaults setDouble:self.petHeight forKey:@"walkOnlyPetSizeV1"];
    for (NSMenuItem *item in sender.menu.itemArray) item.state = (item == sender);

    NSScreen *screen = self.activityScreen ?: [self screenForPanel];
    if (!screen) return;
    NSRect frame = self.panel.frame;
    frame.size = NSMakeSize(self.petHeight * PetAspectRatio, self.petHeight);
    [self.panel setFrame:frame display:YES];
    [self.panel setFrameOrigin:[self clampedOrigin:self.panel.frame.origin onScreen:screen]];
    self.movementX = NSMinX(self.panel.frame);
    self.petView.frame = NSMakeRect(0, 0, NSWidth(frame), NSHeight(frame));
    [self savePosition];
}

- (void)changeSpeed:(NSMenuItem *)sender {
    self.walkingSpeed = [(NSNumber *)sender.representedObject doubleValue];
    [NSUserDefaults.standardUserDefaults setDouble:self.walkingSpeed forKey:@"walkingSpeedV2"];
    for (NSMenuItem *item in sender.menu.itemArray) item.state = (item == sender);
}

- (void)changeMovementMode:(NSMenuItem *)sender {
    self.movesAcrossScreen = [(NSNumber *)sender.representedObject boolValue];
    self.movementX = NSMinX(self.panel.frame);
    [NSUserDefaults.standardUserDefaults setBool:self.movesAcrossScreen forKey:@"movesAcrossScreenV1"];
    self.walkingModeItem.state = self.movesAcrossScreen ? NSControlStateValueOn : NSControlStateValueOff;
    self.steppingModeItem.state = self.movesAcrossScreen ? NSControlStateValueOff : NSControlStateValueOn;
    self.lastUpdate = NSProcessInfo.processInfo.systemUptime;
}

- (void)returnToMainScreen:(id)sender {
    self.activityScreen = NSScreen.mainScreen ?: NSScreen.screens.firstObject;
    [self placeOnGroundNearX:NAN];
    [self savePosition];
    [self.panel orderFrontRegardless];
    if (self.hidden) {
        self.hidden = NO;
        self.visibilityItem.title = @"隐藏艾丝蒂尔";
    }
}

- (void)quit:(id)sender {
    [self savePosition];
    [NSApp terminate:nil];
}
@end

@interface AppDelegate : NSObject <NSApplicationDelegate>
@property(nonatomic, strong) PetController *petController;
@end

@implementation AppDelegate
- (void)applicationDidFinishLaunching:(NSNotification *)notification {
    self.petController = [[PetController alloc] init];
}
- (BOOL)applicationShouldTerminateAfterLastWindowClosed:(NSApplication *)sender { return NO; }
@end

int main(int argc, const char *argv[]) {
    @autoreleasepool {
        NSApplication *application = NSApplication.sharedApplication;
        application.activationPolicy = NSApplicationActivationPolicyAccessory;
        AppDelegate *delegate = [[AppDelegate alloc] init];
        application.delegate = delegate;
        [application run];
    }
    return 0;
}
