import torch
import torch.nn as nn
import numpy as np
import cell_level_search
from genotypes import PRIMITIVES
from genotypes import Genotype
import torch.nn.functional as F
from operations import *
from decode import Decoder

class AutoDeeplab (nn.Module) :
    def __init__(self, num_classes, num_layers, criterion, filter_multiplier = 8, block_multiplier = 5, step = 5, cell=cell_level_search.Cell):
        super(AutoDeeplab, self).__init__()

        self.cells = nn.ModuleList()
        self._num_layers = num_layers
        self._num_classes = num_classes
        self._step = step
        self._block_multiplier = block_multiplier
        self._filter_multiplier = filter_multiplier
        self._criterion = criterion
        self._initialize_alphas_betas ()
        C_initial = 128
        self.stem0 = nn.Sequential(
            nn.Conv2d(3, 64, 3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU ()
        )
        self.stem1 = nn.Sequential(
            nn.Conv2d(64, 64, 3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU ()
        )
        self.stem2 = nn.Sequential(
            nn.Conv2d(64, C_initial, 3, stride=2, padding=1),
            nn.BatchNorm2d(C_initial),
            nn.ReLU ()
        )

        #C_prev_prev = 64
        intitial_fm = C_initial / self._block_multiplier
        for i in range (self._num_layers) :
        # def __init__(self, steps, multiplier, C_prev_prev, C_initial, C, rate) : rate = 0 , 1, 2  reduce rate

            if i == 0 :
                cell1 = cell (self._step, self._block_multiplier, -1, intitial_fm, self._filter_multiplier, 1)
                cell2 = cell (self._step, self._block_multiplier, -1, intitial_fm, self._filter_multiplier * 2, 2)
                self.cells += [cell1]
                self.cells += [cell2]
            elif i == 1 :
                cell1_1 = cell (self._step, self._block_multiplier, intitial_fm, self._filter_multiplier, self._filter_multiplier, 1)
                cell1_2 = cell (self._step, self._block_multiplier, intitial_fm, self._filter_multiplier * 2, self._filter_multiplier, 0)

                cell2_1 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier, self._filter_multiplier * 2, 2)
                cell2_2 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier * 2, self._filter_multiplier * 2, 1)

                cell3 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier * 2, self._filter_multiplier * 4, 2)

                self.cells += [cell1_1]
                self.cells += [cell1_2]
                self.cells += [cell2_1]
                self.cells += [cell2_2]
                self.cells += [cell3]

            elif i == 2 :
                cell1_1 = cell (self._step, self._block_multiplier, self._filter_multiplier, self._filter_multiplier, self._filter_multiplier, 1)
                cell1_2 = cell (self._step, self._block_multiplier, self._filter_multiplier, self._filter_multiplier * 2, self._filter_multiplier, 0)

                cell2_1 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier, self._filter_multiplier * 2, 2)
                cell2_2 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier * 2, self._filter_multiplier * 2, 1)
                cell2_3 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier * 4, self._filter_multiplier * 2, 0)


                cell3_1 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier * 2, self._filter_multiplier * 4, 2)
                cell3_2 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier * 4, self._filter_multiplier * 4, 1)

                cell4 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier * 4, self._filter_multiplier * 8, 2)

                self.cells += [cell1_1]
                self.cells += [cell1_2]
                self.cells += [cell2_1]
                self.cells += [cell2_2]
                self.cells += [cell2_3]
                self.cells += [cell3_1]
                self.cells += [cell3_2]
                self.cells += [cell4]



            elif i == 3 :
                cell1_1 = cell (self._step, self._block_multiplier, self._filter_multiplier, self._filter_multiplier, self._filter_multiplier, 1)
                cell1_2 = cell (self._step, self._block_multiplier, self._filter_multiplier, self._filter_multiplier * 2, self._filter_multiplier, 0)

                cell2_1 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier, self._filter_multiplier * 2, 2)
                cell2_2 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier * 2, self._filter_multiplier * 2, 1)
                cell2_3 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier * 4, self._filter_multiplier * 2, 0)


                cell3_1 = cell (self._step, self._block_multiplier, self._filter_multiplier * 4, self._filter_multiplier * 2, self._filter_multiplier * 4, 2)
                cell3_2 = cell (self._step, self._block_multiplier, self._filter_multiplier * 4, self._filter_multiplier * 4, self._filter_multiplier * 4, 1)
                cell3_3 = cell (self._step, self._block_multiplier, self._filter_multiplier * 4, self._filter_multiplier * 8, self._filter_multiplier * 4, 0)


                cell4_1 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier * 4, self._filter_multiplier * 8, 2)
                cell4_2 = cell (self._step, self._block_multiplier, -1, self._filter_multiplier * 8, self._filter_multiplier * 8, 1)

                self.cells += [cell1_1]
                self.cells += [cell1_2]
                self.cells += [cell2_1]
                self.cells += [cell2_2]
                self.cells += [cell2_3]
                self.cells += [cell3_1]
                self.cells += [cell3_2]
                self.cells += [cell3_3]
                self.cells += [cell4_1]
                self.cells += [cell4_2]

            else :
                cell1_1 = cell (self._step, self._block_multiplier, self._filter_multiplier, self._filter_multiplier, self._filter_multiplier, 1)
                cell1_2 = cell (self._step, self._block_multiplier, self._filter_multiplier, self._filter_multiplier * 2, self._filter_multiplier, 0)

                cell2_1 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier, self._filter_multiplier * 2, 2)
                cell2_2 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier * 2, self._filter_multiplier * 2, 1)
                cell2_3 = cell (self._step, self._block_multiplier, self._filter_multiplier * 2, self._filter_multiplier * 4, self._filter_multiplier * 2, 0)


                cell3_1 = cell (self._step, self._block_multiplier, self._filter_multiplier * 4, self._filter_multiplier * 2, self._filter_multiplier * 4, 2)
                cell3_2 = cell (self._step, self._block_multiplier, self._filter_multiplier * 4, self._filter_multiplier * 4, self._filter_multiplier * 4, 1)
                cell3_3 = cell (self._step, self._block_multiplier, self._filter_multiplier * 4, self._filter_multiplier * 8, self._filter_multiplier * 4, 0)


                cell4_1 = cell (self._step, self._block_multiplier, self._filter_multiplier * 8, self._filter_multiplier * 4, self._filter_multiplier * 8, 2)
                cell4_2 = cell (self._step, self._block_multiplier, self._filter_multiplier * 8, self._filter_multiplier * 8, self._filter_multiplier * 8, 1)

                self.cells += [cell1_1]
                self.cells += [cell1_2]
                self.cells += [cell2_1]
                self.cells += [cell2_2]
                self.cells += [cell2_3]
                self.cells += [cell3_1]
                self.cells += [cell3_2]
                self.cells += [cell3_3]
                self.cells += [cell4_1]
                self.cells += [cell4_2]
        self.aspp_4 = nn.Sequential (
            ASPP (self._block_multiplier * self._filter_multiplier, self._num_classes, 24, 24)
        )
        self.aspp_8 = nn.Sequential (
            ASPP (self._block_multiplier * self._filter_multiplier * 2, self._num_classes, 12, 12)
        )
        self.aspp_16 = nn.Sequential (
            ASPP (self._block_multiplier * self._filter_multiplier * 4, self._num_classes, 6, 6)
        )
        self.aspp_32 = nn.Sequential (
            ASPP (self._block_multiplier * self._filter_multiplier * 8, self._num_classes, 3, 3)
        )



    def forward (self, x) :
        # self._init_level_arr (x)
        self.level_2 = []
        self.level_4 = []
        self.level_8 = []
        self.level_16 = []
        self.level_32 = []
        temp = self.stem0 (x)
        self.level_2.append (self.stem1 (temp))
        self.level_4.append (self.stem2 (self.level_2[-1]))

        count = 0
        img_device = torch.device('cuda', x.get_device())
        self.alphas_cell = self.alphas_cell.to(device=img_device)
        self.bottom_betas = self.bottom_betas.to(device=img_device)
        self.betas8 = self.betas8.to(device=img_device)
        self.betas16 = self.betas16.to(device=img_device)
        self.top_betas = self.top_betas.to(device=img_device)
        normalized_alphas = F.softmax(self.alphas_cell, dim=-1)
        normalized_bottom_betas = F.softmax(self.bottom_betas, dim=-1)
        normalized_betas8 = F.softmax (self.betas8, dim = -1)
        normalized_betas16 = F.softmax(self.betas16, dim=-1)
        normalized_top_betas = F.softmax(self.top_betas, dim=-1)
        for layer in range (self._num_layers - 1) :

            if layer == 0 :
                level4_new = self.cells[count] (None, self.level_4[-1], normalized_alphas)
                count += 1
                level8_new = self.cells[count] (None, self.level_4[-1], normalized_alphas)
                count += 1
                self.level_4.append (level4_new)
                self.level_8.append (level8_new)

            elif layer == 1 :
                level4_new_1 = self.cells[count] (self.level_4[-2], self.level_4[-1], normalized_alphas)
                count += 1
                level4_new_2 = self.cells[count] (self.level_4[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level4_new = normalized_bottom_betas[layer][0] * level4_new_1 + normalized_bottom_betas[layer][1] * level4_new_2

                level8_new_1 = self.cells[count] (None, self.level_4[-1], normalized_alphas)
                count += 1
                level8_new_2 = self.cells[count] (None, self.level_8[-1], normalized_alphas)
                count += 1
                level8_new = normalized_top_betas[layer][0] * level8_new_1 + normalized_top_betas[layer][1] * level8_new_2

                level16_new = self.cells[count] (None, self.level_8[-1], normalized_alphas)
                level16_new = level16_new
                count += 1


                self.level_4.append (level4_new)
                self.level_8.append (level8_new)
                self.level_16.append (level16_new)

            elif layer == 2 :
                level4_new_1 = self.cells[count] (self.level_4[-2], self.level_4[-1], normalized_alphas)
                count += 1
                level4_new_2 = self.cells[count] (self.level_4[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level4_new = normalized_bottom_betas[layer][0] * level4_new_1 + normalized_bottom_betas[layer][1] * level4_new_2

                level8_new_1 = self.cells[count] (self.level_8[-2], self.level_4[-1], normalized_alphas)
                count += 1
                level8_new_2 = self.cells[count] (self.level_8[-2], self.level_8[-1], normalized_alphas)
                count += 1

                level8_new_3 = self.cells[count] (self.level_8[-2], self.level_16[-1], normalized_alphas)
                count += 1
                level8_new = normalized_betas8[layer - 1][0] * level8_new_1 + normalized_betas8[layer - 1][1] * level8_new_2 + normalized_betas8[layer - 1][2] * level8_new_3

                level16_new_1 = self.cells[count] (None, self.level_8[-1], normalized_alphas)
                count += 1
                level16_new_2 = self.cells[count] (None, self.level_16[-1], normalized_alphas)
                count += 1
                level16_new = normalized_top_betas[layer][0] * level16_new_1 + normalized_top_betas[layer][1] * level16_new_2


                level32_new = self.cells[count] (None, self.level_16[-1], normalized_alphas)
                level32_new = level32_new
                count += 1

                self.level_4.append (level4_new)
                self.level_8.append (level8_new)
                self.level_16.append (level16_new)
                self.level_32.append (level32_new)

            elif layer == 3 :
                level4_new_1 = self.cells[count] (self.level_4[-2], self.level_4[-1], normalized_alphas)
                count += 1
                level4_new_2 = self.cells[count] (self.level_4[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level4_new = normalized_bottom_betas[layer][0] * level4_new_1 + normalized_bottom_betas[layer][1] * level4_new_2

                level8_new_1 = self.cells[count] (self.level_8[-2], self.level_4[-1], normalized_alphas)
                count += 1
                level8_new_2 = self.cells[count] (self.level_8[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level8_new_3 = self.cells[count] (self.level_8[-2], self.level_16[-1], normalized_alphas)
                count += 1
                level8_new = normalized_betas8[layer - 1][0] * level8_new_1 + normalized_betas8[layer - 1][1] * level8_new_2 + normalized_betas8[layer - 1][2] * level8_new_3

                level16_new_1 = self.cells[count] (self.level_16[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level16_new_2 = self.cells[count] (self.level_16[-2], self.level_16[-1], normalized_alphas)
                count += 1
                level16_new_3 = self.cells[count] (self.level_16[-2], self.level_32[-1], normalized_alphas)
                count += 1
                level16_new = normalized_betas16[layer - 2][0] * level16_new_1 + normalized_betas16[layer - 2][1] * level16_new_2 + normalized_betas16[layer - 2][2] * level16_new_3


                level32_new_1 = self.cells[count] (None, self.level_16[-1], normalized_alphas)
                count += 1
                level32_new_2 = self.cells[count] (None, self.level_32[-1], normalized_alphas)
                count += 1
                level32_new = normalized_top_betas[layer][0] * level32_new_1 + normalized_top_betas[layer][1] * level32_new_2


                self.level_4.append (level4_new)
                self.level_8.append (level8_new)
                self.level_16.append (level16_new)
                self.level_32.append (level32_new)


            else :
                level4_new_1 = self.cells[count] (self.level_4[-2], self.level_4[-1], normalized_alphas)
                count += 1
                level4_new_2 = self.cells[count] (self.level_4[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level4_new = normalized_bottom_betas[layer][0] * level4_new_1 + normalized_bottom_betas[layer][1] * level4_new_2

                level8_new_1 = self.cells[count] (self.level_8[-2], self.level_4[-1], normalized_alphas)
                count += 1
                level8_new_2 = self.cells[count] (self.level_8[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level8_new_3 = self.cells[count] (self.level_8[-2], self.level_16[-1], normalized_alphas)
                count += 1
                level8_new = normalized_betas8[layer - 1][0] * level8_new_1 + normalized_betas8[layer - 1][1] * level8_new_2 + normalized_betas8[layer - 1][2] * level8_new_3

                level16_new_1 = self.cells[count] (self.level_16[-2], self.level_8[-1], normalized_alphas)
                count += 1
                level16_new_2 = self.cells[count] (self.level_16[-2], self.level_16[-1], normalized_alphas)
                count += 1
                level16_new_3 = self.cells[count] (self.level_16[-2], self.level_32[-1], normalized_alphas)
                count += 1
                level16_new = normalized_betas16[layer - 2][0] * level16_new_1 + normalized_betas16[layer - 2][1] * level16_new_2 + normalized_betas16[layer - 2][2] * level16_new_3


                level32_new_1 = self.cells[count] (self.level_32[-2], self.level_16[-1], normalized_alphas)
                count += 1
                level32_new_2 = self.cells[count] (self.level_32[-2], self.level_32[-1], normalized_alphas)
                count += 1
                level32_new = normalized_top_betas[layer][0] * level32_new_1 + normalized_top_betas[layer][1] * level32_new_2


                self.level_4.append (level4_new)
                self.level_8.append (level8_new)
                self.level_16.append (level16_new)
                self.level_32.append (level32_new)

        aspp_result_4 = self.aspp_4 (self.level_4[-1])
        aspp_result_8 = self.aspp_8 (self.level_8[-1])
        aspp_result_16 = self.aspp_16 (self.level_16[-1])
        aspp_result_32 = self.aspp_32 (self.level_32[-1])
        upsample = nn.Upsample(size=x.size()[2:], mode='bilinear', align_corners=True)
        aspp_result_4 = upsample (aspp_result_4)
        aspp_result_8 = upsample (aspp_result_8)
        aspp_result_16 = upsample (aspp_result_16)
        aspp_result_32 = upsample (aspp_result_32)


        sum_feature_map = aspp_result_4 + aspp_result_8 + aspp_result_16 + aspp_result_32


        return sum_feature_map

    def _initialize_alphas_betas(self):
        k = sum(1 for i in range(self._step) for n in range(2+i))
        num_ops = len(PRIMITIVES)
        self.alphas_cell = torch.tensor (1e-3*torch.randn(k, num_ops).cuda(), requires_grad=True)
        self.bottom_betas = torch.tensor (1e-3 * torch.randn(self._num_layers - 1, 2).cuda(), requires_grad=True)
        self.betas8 = torch.tensor (1e-3 * torch.randn(self._num_layers - 2, 3).cuda(), requires_grad=True)
        self.betas16 = torch.tensor(1e-3 * torch.randn(self._num_layers - 3, 3).cuda(), requires_grad=True)
        self.top_betas = torch.tensor (1e-3 * torch.randn(self._num_layers - 1, 2).cuda(), requires_grad=True)

        self._arch_parameters = [
            self.alphas_cell,
            self.bottom_betas,
            self.betas8,
            self.betas16,
            self.top_betas,
        ]


    def decode_viterbi(self):
        decoder = Decoder(self.bottom_betas, self.betas8, self.betas16, self.top_betas)
        return decoder.viterbi_decode()

    def decode_dfs(self):
        decoder = Decoder(self.bottom_betas, self.betas8, self.betas16, self.top_betas)
        return decoder.dfs_decode()

    def arch_parameters (self) :
        return self._arch_parameters

    def genotype(self):
        def _parse(weights):
            gene = []
            n = 2
            start = 0
            for i in range(self._step):
                end = start + n
                W = weights[start:end].copy()
                edges = sorted (range(i + 2), key=lambda x: -max(W[x][k] for k in range(len(W[x])) if k != PRIMITIVES.index('none')))[:2]
                for j in edges:
                    k_best = None
                    for k in range(len(W[j])):
                        if k != PRIMITIVES.index('none'):
                            if k_best is None or W[j][k] > W[j][k_best]:
                                k_best = k
                    gene.append((PRIMITIVES[k_best], j))
                start = end
                n += 1
            return gene

        gene_cell = _parse(F.softmax(self.alphas_cell, dim=-1).data.cpu().numpy())
        concat = range(2 + self._step - self._block_multiplier, self._step + 2)
        genotype = Genotype(
            cell=gene_cell, cell_concat=concat
        )

        return genotype

    def _loss (self, input, target) :
        logits = self (input)
        return self._criterion (logits, target)


def main () :
    model = AutoDeeplab (7, 12, None)
    x = torch.tensor (torch.ones (4, 3, 224, 224))
    resultdfs = model.decode_dfs ()
    resultviterbi = model.decode_viterbi()[0]


    print (resultviterbi)
    print (model.genotype())

if __name__ == '__main__' :
    main ()
