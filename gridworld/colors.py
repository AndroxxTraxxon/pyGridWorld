import colorsys
from enum import Enum
from random import choice

def clamp(_min, _max, value):
    return max(min(value, _max), _min)

class Color:
    red:int
    green:int
    blue:int
    name:str

    colordict = dict()

    def __init__(self, red=0, green=0, blue=0, name:str=None):
        self.red = int(clamp(0, 255, red))
        self.green = int(clamp(0, 255, green))
        self.blue = int(clamp(0, 255, blue))
        self.name = name

        if name is not None:
            self.__class__.colordict[name.upper()] = self
            self.__class__.colordict[name.lower()] = self
            try:
                setattr(self.__class__, name.upper(), self)
                setattr(self.__class__, name.lower(), self)
            except:
                # oh well, we tried.
                pass
    @property
    def hsv(self) -> tuple:
        return colorsys.rgb_to_hsv(
            self.red/255,
            self.green/255,
            self.blue/255,
        )

    @property
    def hls(self) -> tuple:
        return colorsys.rgb_to_hls(
            self.red/255,
            self.green/255,
            self.blue/255,
        )

    @property
    def yiq(self) -> tuple:
        return colorsys.rgb_to_yiq(
            self.red/255,
            self.green/255,
            self.blue/255,
        )
    
    @property
    def rgb(self) -> tuple:
        return (
            self.red,
            self.green,
            self.blue,
        )

    @classmethod
    def from_hsv(cls, h, s, v):
        red, green, blue = colorsys.hsv_to_rgb(h,s,v)
        return cls(
            int(red * 255),
            int(green * 255),
            int(blue * 255)
        )
    
    @classmethod
    def random(cls):
        return cls.colordict[
            choice(tuple(cls.colordict))
        ]
    
    

    def __str__(self):
        return "#{red:02X}{green:02X}{blue:02X}".format(
            red=self.red,
            green=self.green,
            blue=self.blue
        )
    
    def __repr__(self):
        return"{classname} {name}(R:{r}, G:{g}, b:{b})".format(
            classname=self.__class__.__name__,
            name=self.name if self.name is not None else "",
            r=self.red,
            g=self.green,
            b=self.blue
        )

Color(240, 248, 255, 'ALICEBLUE')
Color(250, 235, 215, 'ANTIQUEWHITE')
Color(255, 239, 219, 'ANTIQUEWHITE1')
Color(238, 223, 204, 'ANTIQUEWHITE2')
Color(205, 192, 176, 'ANTIQUEWHITE3')
Color(139, 131, 120, 'ANTIQUEWHITE4')
Color(0, 255, 255, 'AQUA')
Color(127, 255, 212, 'AQUAMARINE1')
Color(118, 238, 198, 'AQUAMARINE2')
Color(102, 205, 170, 'AQUAMARINE3')
Color(69, 139, 116, 'AQUAMARINE4')
Color(240, 255, 255, 'AZURE1')
Color(224, 238, 238, 'AZURE2')
Color(193, 205, 205, 'AZURE3')
Color(131, 139, 139, 'AZURE4')
Color(227, 207, 87, 'BANANA')
Color(245, 245, 220, 'BEIGE')
Color(255, 228, 196, 'BISQUE1')
Color(238, 213, 183, 'BISQUE2')
Color(205, 183, 158, 'BISQUE3')
Color(139, 125, 107, 'BISQUE4')
Color(0, 0, 0, 'BLACK')
Color(255, 235, 205, 'BLANCHEDALMOND')
Color(0, 0, 255, 'BLUE')
Color(0, 0, 238, 'BLUE2')
Color(0, 0, 205, 'BLUE3')
Color(0, 0, 139, 'BLUE4')
Color(138, 43, 226, 'BLUEVIOLET')
Color(156, 102, 31, 'BRICK')
Color(165, 42, 42, 'BROWN')
Color(255, 64, 64, 'BROWN1')
Color(238, 59, 59, 'BROWN2')
Color(205, 51, 51, 'BROWN3')
Color(139, 35, 35, 'BROWN4')
Color(222, 184, 135, 'BURLYWOOD')
Color(255, 211, 155, 'BURLYWOOD1')
Color(238, 197, 145, 'BURLYWOOD2')
Color(205, 170, 125, 'BURLYWOOD3')
Color(139, 115, 85, 'BURLYWOOD4')
Color(138, 54, 15, 'BURNTSIENNA')
Color(138, 51, 36, 'BURNTUMBER')
Color(95, 158, 160, 'CADETBLUE')
Color(152, 245, 255, 'CADETBLUE1')
Color(142, 229, 238, 'CADETBLUE2')
Color(122, 197, 205, 'CADETBLUE3')
Color(83, 134, 139, 'CADETBLUE4')
Color(255, 97, 3, 'CADMIUMORANGE')
Color(255, 153, 18, 'CADMIUMYELLOW')
Color(237, 145, 33, 'CARROT')
Color(127, 255, 0, 'CHARTREUSE1')
Color(118, 238, 0, 'CHARTREUSE2')
Color(102, 205, 0, 'CHARTREUSE3')
Color(69, 139, 0, 'CHARTREUSE4')
Color(210, 105, 30, 'CHOCOLATE')
Color(255, 127, 36, 'CHOCOLATE1')
Color(238, 118, 33, 'CHOCOLATE2')
Color(205, 102, 29, 'CHOCOLATE3')
Color(139, 69, 19, 'CHOCOLATE4')
Color(61, 89, 171, 'COBALT')
Color(61, 145, 64, 'COBALTGREEN')
Color(128, 138, 135, 'COLDGREY')
Color(255, 127, 80, 'CORAL')
Color(255, 114, 86, 'CORAL1')
Color(238, 106, 80, 'CORAL2')
Color(205, 91, 69, 'CORAL3')
Color(139, 62, 47, 'CORAL4')
Color(100, 149, 237, 'CORNFLOWERBLUE')
Color(255, 248, 220, 'CORNSILK1')
Color(238, 232, 205, 'CORNSILK2')
Color(205, 200, 177, 'CORNSILK3')
Color(139, 136, 120, 'CORNSILK4')
Color(220, 20, 60, 'CRIMSON')
Color(0, 238, 238, 'CYAN2')
Color(0, 205, 205, 'CYAN3')
Color(0, 139, 139, 'CYAN4')
Color(184, 134, 11, 'DARKGOLDENROD')
Color(255, 185, 15, 'DARKGOLDENROD1')
Color(238, 173, 14, 'DARKGOLDENROD2')
Color(205, 149, 12, 'DARKGOLDENROD3')
Color(139, 101, 8, 'DARKGOLDENROD4')
Color(169, 169, 169, 'DARKGRAY')
Color(0, 100, 0, 'DARKGREEN')
Color(189, 183, 107, 'DARKKHAKI')
Color(85, 107, 47, 'DARKOLIVEGREEN')
Color(202, 255, 112, 'DARKOLIVEGREEN1')
Color(188, 238, 104, 'DARKOLIVEGREEN2')
Color(162, 205, 90, 'DARKOLIVEGREEN3')
Color(110, 139, 61, 'DARKOLIVEGREEN4')
Color(255, 140, 0, 'DARKORANGE')
Color(255, 127, 0, 'DARKORANGE1')
Color(238, 118, 0, 'DARKORANGE2')
Color(205, 102, 0, 'DARKORANGE3')
Color(139, 69, 0, 'DARKORANGE4')
Color(153, 50, 204, 'DARKORCHID')
Color(191, 62, 255, 'DARKORCHID1')
Color(178, 58, 238, 'DARKORCHID2')
Color(154, 50, 205, 'DARKORCHID3')
Color(104, 34, 139, 'DARKORCHID4')
Color(233, 150, 122, 'DARKSALMON')
Color(143, 188, 143, 'DARKSEAGREEN')
Color(193, 255, 193, 'DARKSEAGREEN1')
Color(180, 238, 180, 'DARKSEAGREEN2')
Color(155, 205, 155, 'DARKSEAGREEN3')
Color(105, 139, 105, 'DARKSEAGREEN4')
Color(72, 61, 139, 'DARKSLATEBLUE')
Color(47, 79, 79, 'DARKSLATEGRAY')
Color(151, 255, 255, 'DARKSLATEGRAY1')
Color(141, 238, 238, 'DARKSLATEGRAY2')
Color(121, 205, 205, 'DARKSLATEGRAY3')
Color(82, 139, 139, 'DARKSLATEGRAY4')
Color(0, 206, 209, 'DARKTURQUOISE')
Color(148, 0, 211, 'DARKVIOLET')
Color(255, 20, 147, 'DEEPPINK1')
Color(238, 18, 137, 'DEEPPINK2')
Color(205, 16, 118, 'DEEPPINK3')
Color(139, 10, 80, 'DEEPPINK4')
Color(0, 191, 255, 'DEEPSKYBLUE1')
Color(0, 178, 238, 'DEEPSKYBLUE2')
Color(0, 154, 205, 'DEEPSKYBLUE3')
Color(0, 104, 139, 'DEEPSKYBLUE4')
Color(105, 105, 105, 'DIMGRAY')
Color(105, 105, 105, 'DIMGRAY')
Color(30, 144, 255, 'DODGERBLUE1')
Color(28, 134, 238, 'DODGERBLUE2')
Color(24, 116, 205, 'DODGERBLUE3')
Color(16, 78, 139, 'DODGERBLUE4')
Color(252, 230, 201, 'EGGSHELL')
Color(0, 201, 87, 'EMERALDGREEN')
Color(178, 34, 34, 'FIREBRICK')
Color(255, 48, 48, 'FIREBRICK1')
Color(238, 44, 44, 'FIREBRICK2')
Color(205, 38, 38, 'FIREBRICK3')
Color(139, 26, 26, 'FIREBRICK4')
Color(255, 125, 64, 'FLESH')
Color(255, 250, 240, 'FLORALWHITE')
Color(34, 139, 34, 'FORESTGREEN')
Color(220, 220, 220, 'GAINSBORO')
Color(248, 248, 255, 'GHOSTWHITE')
Color(255, 215, 0, 'GOLD1')
Color(238, 201, 0, 'GOLD2')
Color(205, 173, 0, 'GOLD3')
Color(139, 117, 0, 'GOLD4')
Color(218, 165, 32, 'GOLDENROD')
Color(255, 193, 37, 'GOLDENROD1')
Color(238, 180, 34, 'GOLDENROD2')
Color(205, 155, 29, 'GOLDENROD3')
Color(139, 105, 20, 'GOLDENROD4')
Color(128, 128, 128, 'GRAY')
Color(3, 3, 3, 'GRAY1')
Color(5, 5, 5, 'GRAY2')
Color(8, 8, 8, 'GRAY3')
Color(10, 10, 10, 'GRAY4')
Color(13, 13, 13, 'GRAY5')
Color(15, 15, 15, 'GRAY6')
Color(18, 18, 18, 'GRAY7')
Color(20, 20, 20, 'GRAY8')
Color(23, 23, 23, 'GRAY9')
Color(26, 26, 26, 'GRAY10')
Color(28, 28, 28, 'GRAY11')
Color(31, 31, 31, 'GRAY12')
Color(33, 33, 33, 'GRAY13')
Color(36, 36, 36, 'GRAY14')
Color(38, 38, 38, 'GRAY15')
Color(41, 41, 41, 'GRAY16')
Color(43, 43, 43, 'GRAY17')
Color(46, 46, 46, 'GRAY18')
Color(48, 48, 48, 'GRAY19')
Color(51, 51, 51, 'GRAY20')
Color(54, 54, 54, 'GRAY21')
Color(56, 56, 56, 'GRAY22')
Color(59, 59, 59, 'GRAY23')
Color(61, 61, 61, 'GRAY24')
Color(64, 64, 64, 'GRAY25')
Color(66, 66, 66, 'GRAY26')
Color(69, 69, 69, 'GRAY27')
Color(71, 71, 71, 'GRAY28')
Color(74, 74, 74, 'GRAY29')
Color(77, 77, 77, 'GRAY30')
Color(79, 79, 79, 'GRAY31')
Color(82, 82, 82, 'GRAY32')
Color(84, 84, 84, 'GRAY33')
Color(87, 87, 87, 'GRAY34')
Color(89, 89, 89, 'GRAY35')
Color(92, 92, 92, 'GRAY36')
Color(94, 94, 94, 'GRAY37')
Color(97, 97, 97, 'GRAY38')
Color(99, 99, 99, 'GRAY39')
Color(102, 102, 102, 'GRAY40')
Color(107, 107, 107, 'GRAY42')
Color(110, 110, 110, 'GRAY43')
Color(112, 112, 112, 'GRAY44')
Color(115, 115, 115, 'GRAY45')
Color(117, 117, 117, 'GRAY46')
Color(120, 120, 120, 'GRAY47')
Color(122, 122, 122, 'GRAY48')
Color(125, 125, 125, 'GRAY49')
Color(127, 127, 127, 'GRAY50')
Color(130, 130, 130, 'GRAY51')
Color(133, 133, 133, 'GRAY52')
Color(135, 135, 135, 'GRAY53')
Color(138, 138, 138, 'GRAY54')
Color(140, 140, 140, 'GRAY55')
Color(143, 143, 143, 'GRAY56')
Color(145, 145, 145, 'GRAY57')
Color(148, 148, 148, 'GRAY58')
Color(150, 150, 150, 'GRAY59')
Color(153, 153, 153, 'GRAY60')
Color(156, 156, 156, 'GRAY61')
Color(158, 158, 158, 'GRAY62')
Color(161, 161, 161, 'GRAY63')
Color(163, 163, 163, 'GRAY64')
Color(166, 166, 166, 'GRAY65')
Color(168, 168, 168, 'GRAY66')
Color(171, 171, 171, 'GRAY67')
Color(173, 173, 173, 'GRAY68')
Color(176, 176, 176, 'GRAY69')
Color(179, 179, 179, 'GRAY70')
Color(181, 181, 181, 'GRAY71')
Color(184, 184, 184, 'GRAY72')
Color(186, 186, 186, 'GRAY73')
Color(189, 189, 189, 'GRAY74')
Color(191, 191, 191, 'GRAY75')
Color(194, 194, 194, 'GRAY76')
Color(196, 196, 196, 'GRAY77')
Color(199, 199, 199, 'GRAY78')
Color(201, 201, 201, 'GRAY79')
Color(204, 204, 204, 'GRAY80')
Color(207, 207, 207, 'GRAY81')
Color(209, 209, 209, 'GRAY82')
Color(212, 212, 212, 'GRAY83')
Color(214, 214, 214, 'GRAY84')
Color(217, 217, 217, 'GRAY85')
Color(219, 219, 219, 'GRAY86')
Color(222, 222, 222, 'GRAY87')
Color(224, 224, 224, 'GRAY88')
Color(227, 227, 227, 'GRAY89')
Color(229, 229, 229, 'GRAY90')
Color(232, 232, 232, 'GRAY91')
Color(235, 235, 235, 'GRAY92')
Color(237, 237, 237, 'GRAY93')
Color(240, 240, 240, 'GRAY94')
Color(242, 242, 242, 'GRAY95')
Color(247, 247, 247, 'GRAY97')
Color(250, 250, 250, 'GRAY98')
Color(252, 252, 252, 'GRAY99')
Color(0, 128, 0, 'GREEN')
Color(0, 255, 0, 'GREEN1')
Color(0, 238, 0, 'GREEN2')
Color(0, 205, 0, 'GREEN3')
Color(0, 139, 0, 'GREEN4')
Color(173, 255, 47, 'GREENYELLOW')
Color(240, 255, 240, 'HONEYDEW1')
Color(224, 238, 224, 'HONEYDEW2')
Color(193, 205, 193, 'HONEYDEW3')
Color(131, 139, 131, 'HONEYDEW4')
Color(255, 105, 180, 'HOTPINK')
Color(255, 110, 180, 'HOTPINK1')
Color(238, 106, 167, 'HOTPINK2')
Color(205, 96, 144, 'HOTPINK3')
Color(139, 58, 98, 'HOTPINK4')
Color(176, 23, 31, 'INDIANRED')
Color(205, 92, 92, 'INDIANRED')
Color(255, 106, 106, 'INDIANRED1')
Color(238, 99, 99, 'INDIANRED2')
Color(205, 85, 85, 'INDIANRED3')
Color(139, 58, 58, 'INDIANRED4')
Color(75, 0, 130, 'INDIGO')
Color(255, 255, 240, 'IVORY1')
Color(238, 238, 224, 'IVORY2')
Color(205, 205, 193, 'IVORY3')
Color(139, 139, 131, 'IVORY4')
Color(41, 36, 33, 'IVORYBLACK')
Color(240, 230, 140, 'KHAKI')
Color(255, 246, 143, 'KHAKI1')
Color(238, 230, 133, 'KHAKI2')
Color(205, 198, 115, 'KHAKI3')
Color(139, 134, 78, 'KHAKI4')
Color(230, 230, 250, 'LAVENDER')
Color(255, 240, 245, 'LAVENDERBLUSH1')
Color(238, 224, 229, 'LAVENDERBLUSH2')
Color(205, 193, 197, 'LAVENDERBLUSH3')
Color(139, 131, 134, 'LAVENDERBLUSH4')
Color(124, 252, 0, 'LAWNGREEN')
Color(255, 250, 205, 'LEMONCHIFFON1')
Color(238, 233, 191, 'LEMONCHIFFON2')
Color(205, 201, 165, 'LEMONCHIFFON3')
Color(139, 137, 112, 'LEMONCHIFFON4')
Color(173, 216, 230, 'LIGHTBLUE')
Color(191, 239, 255, 'LIGHTBLUE1')
Color(178, 223, 238, 'LIGHTBLUE2')
Color(154, 192, 205, 'LIGHTBLUE3')
Color(104, 131, 139, 'LIGHTBLUE4')
Color(240, 128, 128, 'LIGHTCORAL')
Color(224, 255, 255, 'LIGHTCYAN1')
Color(209, 238, 238, 'LIGHTCYAN2')
Color(180, 205, 205, 'LIGHTCYAN3')
Color(122, 139, 139, 'LIGHTCYAN4')
Color(255, 236, 139, 'LIGHTGOLDENROD1')
Color(238, 220, 130, 'LIGHTGOLDENROD2')
Color(205, 190, 112, 'LIGHTGOLDENROD3')
Color(139, 129, 76, 'LIGHTGOLDENROD4')
Color(250, 250, 210, 'LIGHTGOLDENRODYELLOW')
Color(211, 211, 211, 'LIGHTGREY')
Color(255, 182, 193, 'LIGHTPINK')
Color(255, 174, 185, 'LIGHTPINK1')
Color(238, 162, 173, 'LIGHTPINK2')
Color(205, 140, 149, 'LIGHTPINK3')
Color(139, 95, 101, 'LIGHTPINK4')
Color(255, 160, 122, 'LIGHTSALMON1')
Color(238, 149, 114, 'LIGHTSALMON2')
Color(205, 129, 98, 'LIGHTSALMON3')
Color(139, 87, 66, 'LIGHTSALMON4')
Color(32, 178, 170, 'LIGHTSEAGREEN')
Color(135, 206, 250, 'LIGHTSKYBLUE')
Color(176, 226, 255, 'LIGHTSKYBLUE1')
Color(164, 211, 238, 'LIGHTSKYBLUE2')
Color(141, 182, 205, 'LIGHTSKYBLUE3')
Color(96, 123, 139, 'LIGHTSKYBLUE4')
Color(132, 112, 255, 'LIGHTSLATEBLUE')
Color(119, 136, 153, 'LIGHTSLATEGRAY')
Color(176, 196, 222, 'LIGHTSTEELBLUE')
Color(202, 225, 255, 'LIGHTSTEELBLUE1')
Color(188, 210, 238, 'LIGHTSTEELBLUE2')
Color(162, 181, 205, 'LIGHTSTEELBLUE3')
Color(110, 123, 139, 'LIGHTSTEELBLUE4')
Color(255, 255, 224, 'LIGHTYELLOW1')
Color(238, 238, 209, 'LIGHTYELLOW2')
Color(205, 205, 180, 'LIGHTYELLOW3')
Color(139, 139, 122, 'LIGHTYELLOW4')
Color(50, 205, 50, 'LIMEGREEN')
Color(250, 240, 230, 'LINEN')
Color(255, 0, 255, 'MAGENTA')
Color(238, 0, 238, 'MAGENTA2')
Color(205, 0, 205, 'MAGENTA3')
Color(139, 0, 139, 'MAGENTA4')
Color(3, 168, 158, 'MANGANESEBLUE')
Color(128, 0, 0, 'MAROON')
Color(255, 52, 179, 'MAROON1')
Color(238, 48, 167, 'MAROON2')
Color(205, 41, 144, 'MAROON3')
Color(139, 28, 98, 'MAROON4')
Color(186, 85, 211, 'MEDIUMORCHID')
Color(224, 102, 255, 'MEDIUMORCHID1')
Color(209, 95, 238, 'MEDIUMORCHID2')
Color(180, 82, 205, 'MEDIUMORCHID3')
Color(122, 55, 139, 'MEDIUMORCHID4')
Color(147, 112, 219, 'MEDIUMPURPLE')
Color(171, 130, 255, 'MEDIUMPURPLE1')
Color(159, 121, 238, 'MEDIUMPURPLE2')
Color(137, 104, 205, 'MEDIUMPURPLE3')
Color(93, 71, 139, 'MEDIUMPURPLE4')
Color(60, 179, 113, 'MEDIUMSEAGREEN')
Color(123, 104, 238, 'MEDIUMSLATEBLUE')
Color(0, 250, 154, 'MEDIUMSPRINGGREEN')
Color(72, 209, 204, 'MEDIUMTURQUOISE')
Color(199, 21, 133, 'MEDIUMVIOLETRED')
Color(227, 168, 105, 'MELON')
Color(25, 25, 112, 'MIDNIGHTBLUE')
Color(189, 252, 201, 'MINT')
Color(245, 255, 250, 'MINTCREAM')
Color(255, 228, 225, 'MISTYROSE1')
Color(238, 213, 210, 'MISTYROSE2')
Color(205, 183, 181, 'MISTYROSE3')
Color(139, 125, 123, 'MISTYROSE4')
Color(255, 228, 181, 'MOCCASIN')
Color(255, 222, 173, 'NAVAJOWHITE1')
Color(238, 207, 161, 'NAVAJOWHITE2')
Color(205, 179, 139, 'NAVAJOWHITE3')
Color(139, 121, 94, 'NAVAJOWHITE4')
Color(0, 0, 128, 'NAVY')
Color(253, 245, 230, 'OLDLACE')
Color(128, 128, 0, 'OLIVE')
Color(107, 142, 35, 'OLIVEDRAB')
Color(192, 255, 62, 'OLIVEDRAB1')
Color(179, 238, 58, 'OLIVEDRAB2')
Color(154, 205, 50, 'OLIVEDRAB3')
Color(105, 139, 34, 'OLIVEDRAB4')
Color(255, 128, 0, 'ORANGE')
Color(255, 165, 0, 'ORANGE1')
Color(238, 154, 0, 'ORANGE2')
Color(205, 133, 0, 'ORANGE3')
Color(139, 90, 0, 'ORANGE4')
Color(255, 69, 0, 'ORANGERED1')
Color(238, 64, 0, 'ORANGERED2')
Color(205, 55, 0, 'ORANGERED3')
Color(139, 37, 0, 'ORANGERED4')
Color(218, 112, 214, 'ORCHID')
Color(255, 131, 250, 'ORCHID1')
Color(238, 122, 233, 'ORCHID2')
Color(205, 105, 201, 'ORCHID3')
Color(139, 71, 137, 'ORCHID4')
Color(238, 232, 170, 'PALEGOLDENROD')
Color(152, 251, 152, 'PALEGREEN')
Color(154, 255, 154, 'PALEGREEN1')
Color(144, 238, 144, 'PALEGREEN2')
Color(124, 205, 124, 'PALEGREEN3')
Color(84, 139, 84, 'PALEGREEN4')
Color(187, 255, 255, 'PALETURQUOISE1')
Color(174, 238, 238, 'PALETURQUOISE2')
Color(150, 205, 205, 'PALETURQUOISE3')
Color(102, 139, 139, 'PALETURQUOISE4')
Color(219, 112, 147, 'PALEVIOLETRED')
Color(255, 130, 171, 'PALEVIOLETRED1')
Color(238, 121, 159, 'PALEVIOLETRED2')
Color(205, 104, 137, 'PALEVIOLETRED3')
Color(139, 71, 93, 'PALEVIOLETRED4')
Color(255, 239, 213, 'PAPAYAWHIP')
Color(255, 218, 185, 'PEACHPUFF1')
Color(238, 203, 173, 'PEACHPUFF2')
Color(205, 175, 149, 'PEACHPUFF3')
Color(139, 119, 101, 'PEACHPUFF4')
Color(51, 161, 201, 'PEACOCK')
Color(255, 192, 203, 'PINK')
Color(255, 181, 197, 'PINK1')
Color(238, 169, 184, 'PINK2')
Color(205, 145, 158, 'PINK3')
Color(139, 99, 108, 'PINK4')
Color(221, 160, 221, 'PLUM')
Color(255, 187, 255, 'PLUM1')
Color(238, 174, 238, 'PLUM2')
Color(205, 150, 205, 'PLUM3')
Color(139, 102, 139, 'PLUM4')
Color(176, 224, 230, 'POWDERBLUE')
Color(128, 0, 128, 'PURPLE')
Color(155, 48, 255, 'PURPLE1')
Color(145, 44, 238, 'PURPLE2')
Color(125, 38, 205, 'PURPLE3')
Color(85, 26, 139, 'PURPLE4')
Color(135, 38, 87, 'RASPBERRY')
Color(199, 97, 20, 'RAWSIENNA')
Color(255, 0, 0, 'RED')
Color(255, 0, 0, 'RED1')
Color(238, 0, 0, 'RED2')
Color(205, 0, 0, 'RED3')
Color(139, 0, 0, 'RED4')
Color(188, 143, 143, 'ROSYBROWN')
Color(255, 193, 193, 'ROSYBROWN1')
Color(238, 180, 180, 'ROSYBROWN2')
Color(205, 155, 155, 'ROSYBROWN3')
Color(139, 105, 105, 'ROSYBROWN4')
Color(65, 105, 225, 'ROYALBLUE')
Color(72, 118, 255, 'ROYALBLUE1')
Color(67, 110, 238, 'ROYALBLUE2')
Color(58, 95, 205, 'ROYALBLUE3')
Color(39, 64, 139, 'ROYALBLUE4')
Color(250, 128, 114, 'SALMON')
Color(255, 140, 105, 'SALMON1')
Color(238, 130, 98, 'SALMON2')
Color(205, 112, 84, 'SALMON3')
Color(139, 76, 57, 'SALMON4')
Color(244, 164, 96, 'SANDYBROWN')
Color(48, 128, 20, 'SAPGREEN')
Color(84, 255, 159, 'SEAGREEN1')
Color(78, 238, 148, 'SEAGREEN2')
Color(67, 205, 128, 'SEAGREEN3')
Color(46, 139, 87, 'SEAGREEN4')
Color(255, 245, 238, 'SEASHELL1')
Color(238, 229, 222, 'SEASHELL2')
Color(205, 197, 191, 'SEASHELL3')
Color(139, 134, 130, 'SEASHELL4')
Color(94, 38, 18, 'SEPIA')
Color(142, 56, 142, 'SGIBEET')
Color(197, 193, 170, 'SGIBRIGHTGRAY')
Color(113, 198, 113, 'SGICHARTREUSE')
Color(85, 85, 85, 'SGIDARKGRAY')
Color(30, 30, 30, 'SGIGRAY12')
Color(40, 40, 40, 'SGIGRAY16')
Color(81, 81, 81, 'SGIGRAY32')
Color(91, 91, 91, 'SGIGRAY36')
Color(132, 132, 132, 'SGIGRAY52')
Color(142, 142, 142, 'SGIGRAY56')
Color(183, 183, 183, 'SGIGRAY72')
Color(193, 193, 193, 'SGIGRAY76')
Color(234, 234, 234, 'SGIGRAY92')
Color(244, 244, 244, 'SGIGRAY96')
Color(125, 158, 192, 'SGILIGHTBLUE')
Color(170, 170, 170, 'SGILIGHTGRAY')
Color(142, 142, 56, 'SGIOLIVEDRAB')
Color(198, 113, 113, 'SGISALMON')
Color(113, 113, 198, 'SGISLATEBLUE')
Color(56, 142, 142, 'SGITEAL')
Color(160, 82, 45, 'SIENNA')
Color(255, 130, 71, 'SIENNA1')
Color(238, 121, 66, 'SIENNA2')
Color(205, 104, 57, 'SIENNA3')
Color(139, 71, 38, 'SIENNA4')
Color(192, 192, 192, 'SILVER')
Color(135, 206, 235, 'SKYBLUE')
Color(135, 206, 255, 'SKYBLUE1')
Color(126, 192, 238, 'SKYBLUE2')
Color(108, 166, 205, 'SKYBLUE3')
Color(74, 112, 139, 'SKYBLUE4')
Color(106, 90, 205, 'SLATEBLUE')
Color(131, 111, 255, 'SLATEBLUE1')
Color(122, 103, 238, 'SLATEBLUE2')
Color(105, 89, 205, 'SLATEBLUE3')
Color(71, 60, 139, 'SLATEBLUE4')
Color(112, 128, 144, 'SLATEGRAY')
Color(198, 226, 255, 'SLATEGRAY1')
Color(185, 211, 238, 'SLATEGRAY2')
Color(159, 182, 205, 'SLATEGRAY3')
Color(108, 123, 139, 'SLATEGRAY4')
Color(255, 250, 250, 'SNOW1')
Color(238, 233, 233, 'SNOW2')
Color(205, 201, 201, 'SNOW3')
Color(139, 137, 137, 'SNOW4')
Color(0, 255, 127, 'SPRINGGREEN')
Color(0, 238, 118, 'SPRINGGREEN1')
Color(0, 205, 102, 'SPRINGGREEN2')
Color(0, 139, 69, 'SPRINGGREEN3')
Color(70, 130, 180, 'STEELBLUE')
Color(99, 184, 255, 'STEELBLUE1')
Color(92, 172, 238, 'STEELBLUE2')
Color(79, 148, 205, 'STEELBLUE3')
Color(54, 100, 139, 'STEELBLUE4')
Color(210, 180, 140, 'TAN')
Color(255, 165, 79, 'TAN1')
Color(238, 154, 73, 'TAN2')
Color(205, 133, 63, 'TAN3')
Color(139, 90, 43, 'TAN4')
Color(0, 128, 128, 'TEAL')
Color(216, 191, 216, 'THISTLE')
Color(255, 225, 255, 'THISTLE1')
Color(238, 210, 238, 'THISTLE2')
Color(205, 181, 205, 'THISTLE3')
Color(139, 123, 139, 'THISTLE4')
Color(255, 99, 71, 'TOMATO1')
Color(238, 92, 66, 'TOMATO2')
Color(205, 79, 57, 'TOMATO3')
Color(139, 54, 38, 'TOMATO4')
Color(64, 224, 208, 'TURQUOISE')
Color(0, 245, 255, 'TURQUOISE1')
Color(0, 229, 238, 'TURQUOISE2')
Color(0, 197, 205, 'TURQUOISE3')
Color(0, 134, 139, 'TURQUOISE4')
Color(0, 199, 140, 'TURQUOISEBLUE')
Color(238, 130, 238, 'VIOLET')
Color(208, 32, 144, 'VIOLETRED')
Color(255, 62, 150, 'VIOLETRED1')
Color(238, 58, 140, 'VIOLETRED2')
Color(205, 50, 120, 'VIOLETRED3')
Color(139, 34, 82, 'VIOLETRED4')
Color(128, 128, 105, 'WARMGREY')
Color(245, 222, 179, 'WHEAT')
Color(255, 231, 186, 'WHEAT1')
Color(238, 216, 174, 'WHEAT2')
Color(205, 186, 150, 'WHEAT3')
Color(139, 126, 102, 'WHEAT4')
Color(255, 255, 255, 'WHITE')
Color(245, 245, 245, 'WHITESMOKE')
Color(255, 255, 0, 'YELLOW1')
Color(238, 238, 0, 'YELLOW2')
Color(205, 205, 0, 'YELLOW3')
Color(139, 139, 0, 'YELLOW4')

colors = Color.colordict