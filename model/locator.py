from model.HR_Net.seg_hrnet import get_seg_model
from model.VGG.VGG16_FPN import VGG16_FPN
import torch.nn as nn
import torch.nn.functional as F
import torch
import numpy as np
from model.PBM import BinarizedModule
from torchvision import models
import torch
from torchsummary import summary


class Crowd_locator(nn.Module):
    def __init__(self, net_name, gpu_id, pretrained=True):
        super(Crowd_locator, self).__init__()

        if net_name == 'HR_Net':
            self.Extractor = get_seg_model()
            self.Binar = BinarizedModule(input_channels=720)
        if net_name == 'VGG16_FPN':
            self.Extractor = VGG16_FPN()
            self.Binar = BinarizedModule(input_channels=768)

        if len(gpu_id) > 1:
            self.Extractor = torch.nn.DataParallel(self.Extractor).cuda()
            self.Binar = torch.nn.DataParallel(self.Binar).cuda()
        else:
            self.Extractor = self.Extractor.cuda()
            self.Binar = self.Binar.cuda()

        self.loss_BCE = nn.BCELoss().cuda()

    @property
    def loss(self):
        return  self.head_map_loss, self.binar_map_loss

    def forward(self, img, mask_gt, mode = 'train'):
        # print(size_map_gt.max())
        #get_seg_model，返回为
        feature, pre_map = self.Extractor(img)
        #BinarizedModule，返回为阈值图与二值化图
        threshold_matrix, binar_map = self.Binar(feature,pre_map)

        if mode == 'train':
        # weight = torch.ones_like(binar_map).cuda()
        # weight[mask_gt==1] = 2
            assert pre_map.size(2) == mask_gt.size(2)
            self.binar_map_loss = (torch.abs(binar_map-mask_gt)).mean()

            self.head_map_loss = F.mse_loss(pre_map, mask_gt)
  
        return threshold_matrix, pre_map ,binar_map

    def test_forward(self, img):
        feature, pre_map = self.Extractor(img)

        return feature, pre_map


if __name__ == '__main__':


    model = Res_FPN(pretrained = False).cuda()
    summary(model,(3,24,24))

