import torch
import torch.nn.functional as F

from . import bbox


def assign_gt_to_priors(gtboxes, priors, low_thr, high_thr, match_low_quality):
    """"""
    m = bbox.calc_iou_matrix(gtboxes, priors)
    v, idx = m.max(dim=0)
    idx += 1
    if match_low_quality:
        copied = idx.clone()
    idx[v < low_thr] = 0
    idx[(v >= low_thr) & (v < high_thr)] = -1
    if match_low_quality:
        maxgt = m.max(dim=1)[0]
        extra = torch.where(m == maxgt[:, None])[1]
        idx[extra] = copied[extra]
    return idx


def random_balanced_sampler(gtidx, num, pos_fraction):
    pos = torch.nonzero(gtidx >= 1).squeeze()
    neg = torch.nonzero(gtidx == 0).squeeze()
    np = min(pos.numel(), int(256 * 0.5))
    nn = min(neg.numel(), 256 - np)
    perm1 = torch.randperm(pos.numel())[:np]
    perm2 = torch.randperm(neg.numel())[:nn]
    perm1 = torch.sort(perm1)[0]
    perm2 = torch.sort(perm2)[0]
    return pos[perm1], neg[perm2]


def get_losses(gtboxes, priors, regs, logs):
    lg, lb, inp, trg = [], [], [], []
    for i in range(len(gtboxes)):
        gtidx = assign_gt_to_priors(gtboxes[i], priors, 0.3, 0.7, True)
        pos, neg = random_balanced_sampler(gtidx, 256, 0.5)
        all_ = torch.cat([pos, neg])
        #print(logs[i][:5])
        logits = logs[i][all_].squeeze()
        labels = gtidx[all_].clamp(max=1)
        inputs = regs[i][pos]
        targets = bbox.encode(gtboxes[i][gtidx[pos] - 1], priors[pos], (1, 1, 1, 1))
        lg.append(logits)
        lb.append(labels)
        inp.append(inputs)
        trg.append(targets)
    lg, lb, inp, trg = [torch.cat(x) for x in [lg, lb, inp, trg]]
    #print(lg.shape, lg[:20])
    #print(lb.shape, lb[:20])
    loss_obj = F.binary_cross_entropy_with_logits(lg, lb.to(torch.float32))
    loss_reg = F.smooth_l1_loss(inp, trg, beta=1/9, reduction='sum') / (lg.numel())
    return loss_obj, loss_reg