import torch
import torch.nn as nn


class ConvUnit(nn.Module):

    def __init__(self, cin, cout, k, s, p, activ, bn=1e-05, grp=1, d=1):
        super().__init__()

        cin, cout, grp = int(cin), int(cout), int(grp)
        self.conv = nn.Conv2d(cin, cout, k, s, p, groups=grp, bias=bn is None, dilation=d)
        
        if bn == None:
            self.bn = None
        elif isinstance(bn, tuple) and bn[1] == 'frozen':
            self.bn = nn.BatchNorm2d(cout, eps=bn[0])
            self.bn.training = False
        else:
            self.bn = nn.BatchNorm2d(cout, eps=bn)

        if activ == None:
            self.activ = None
        elif activ == 'relu':
            self.activ = nn.ReLU(inplace=True)
        elif activ == 'relu6':
            self.activ = nn.ReLU6(inplace=True)
        elif activ == 'prelu':
            self.activ = nn.PReLU(cout)
        elif activ.startswith('lrelu'):
            leak = float(activ.split('_')[1])
            self.activ = nn.LeakyReLU(leak, inplace=True)
        elif activ == 'hardswish':
            self.activ = nn.Hardswish()

    def forward(self, x):
        x = self.conv(x)
        if self.bn:
            x = self.bn(x)
        if self.activ:
            x = self.activ(x)
        return x


class BaseMultiReturn(nn.Module):
    """A base class for a sequential network that can return intermediate layers' results.
    It must have self.layers = nn.Sequential(<modules>) and retidx = indices of needed modules.
    If retidx = None, then it returns only the final result as usual, and if
    max(retidx) < last layer index, then it won't waste resources on running the remaining modules.
    """

    def __init__(self, retidx=None):
        super().__init__()
        self.retidx = retidx
    
    def forward(self, x):
        if not self.retidx:
            return self.layers(x)
        xs = []
        for i in range(max(self.retidx) + 1):
            x = self.layers[i](x)
            if i in self.retidx:
                xs.append(x)
        return xs