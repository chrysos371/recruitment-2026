"""E4 VGG-16 vs ResNet-18 — AutoDL optimized version (HF datasets)"""
import torch, torch.nn as nn, torch.optim as optim, numpy as np, time, os, sys, argparse
from torch.utils.data import DataLoader
from datasets import load_dataset
import torchvision.transforms as transforms

# ======================== MODELS ========================
class VGG16(nn.Module):
    def __init__(self, num_classes=10):
        super().__init__()
        def conv_block(in_c, out_c, n):
            layers = []
            for _ in range(n):
                layers += [nn.Conv2d(in_c, out_c, 3, padding=1), nn.BatchNorm2d(out_c), nn.ReLU(inplace=True)]
                in_c = out_c
            layers.append(nn.MaxPool2d(2,2))
            return nn.Sequential(*layers)
        self.block1 = conv_block(3, 64, 2)
        self.block2 = conv_block(64, 128, 2)
        self.block3 = conv_block(128, 256, 3)
        self.block4 = conv_block(256, 512, 3)
        self.block5 = conv_block(512, 512, 3)
        self.classifier = nn.Sequential(nn.Dropout(0.5), nn.Linear(512,512), nn.ReLU(inplace=True), nn.Dropout(0.5), nn.Linear(512,num_classes))
        for m in self.modules():
            if isinstance(m, nn.Conv2d): nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
            elif isinstance(m, nn.BatchNorm2d): nn.init.constant_(m.weight,1); nn.init.constant_(m.bias,0)
            elif isinstance(m, nn.Linear): nn.init.normal_(m.weight,0,0.01); nn.init.constant_(m.bias,0)
    def forward(self,x):
        for b in [self.block1,self.block2,self.block3,self.block4,self.block5]: x=b(x)
        return self.classifier(x.view(x.size(0),-1))

class BasicBlock(nn.Module):
    expansion=1
    def __init__(self,in_planes,planes,stride=1):
        super().__init__()
        self.conv1=nn.Conv2d(in_planes,planes,3,stride=stride,padding=1,bias=False); self.bn1=nn.BatchNorm2d(planes)
        self.conv2=nn.Conv2d(planes,planes,3,stride=1,padding=1,bias=False); self.bn2=nn.BatchNorm2d(planes)
        self.shortcut=nn.Sequential()
        if stride!=1 or in_planes!=self.expansion*planes:
            self.shortcut=nn.Sequential(nn.Conv2d(in_planes,self.expansion*planes,1,stride=stride,bias=False),nn.BatchNorm2d(self.expansion*planes))
    def forward(self,x):
        out=torch.relu(self.bn1(self.conv1(x))); out=self.bn2(self.conv2(out)); out+=self.shortcut(x); return torch.relu(out)

class ResNet18(nn.Module):
    def __init__(self,num_classes=10):
        super().__init__(); self.in_planes=64
        self.conv1=nn.Conv2d(3,64,3,stride=1,padding=1,bias=False); self.bn1=nn.BatchNorm2d(64)
        self.layer1=self._make_layer(64,2,stride=1); self.layer2=self._make_layer(128,2,stride=2)
        self.layer3=self._make_layer(256,2,stride=2); self.layer4=self._make_layer(512,2,stride=2)
        self.avgpool=nn.AdaptiveAvgPool2d((1,1)); self.fc=nn.Linear(512*BasicBlock.expansion,num_classes)
        for m in self.modules():
            if isinstance(m,nn.Conv2d): nn.init.kaiming_normal_(m.weight,mode='fan_out',nonlinearity='relu')
            elif isinstance(m,nn.BatchNorm2d): nn.init.constant_(m.weight,1); nn.init.constant_(m.bias,0)
            elif isinstance(m,nn.Linear): nn.init.constant_(m.bias,0)
    def _make_layer(self,planes,num_blocks,stride):
        layers=[BasicBlock(self.in_planes,planes,stride)]; self.in_planes=planes*BasicBlock.expansion
        for _ in range(1,num_blocks): layers.append(BasicBlock(self.in_planes,planes))
        return nn.Sequential(*layers)
    def forward(self,x):
        out=torch.relu(self.bn1(self.conv1(x))); out=self.layer1(out); out=self.layer2(out)
        out=self.layer3(out); out=self.layer4(out); out=self.avgpool(out)
        return self.fc(out.view(out.size(0),-1))

# ======================== DATA ========================
class HFDataset(torch.utils.data.Dataset):
    def __init__(self, hf_ds, transform=None):
        self.data = hf_ds; self.transform = transform
    def __len__(self): return len(self.data)
    def __getitem__(self, idx):
        item = self.data[idx]; img = item['img'].convert('RGB')
        if self.transform: img = self.transform(img)
        return img, item['label']

def get_cifar10(batch_size=128):
    os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
    ds = load_dataset('uoft-cs/cifar10', cache_dir='/root/data')
    transform_train = transforms.Compose([
        transforms.RandomCrop(32,padding=4), transforms.RandomHorizontalFlip(), transforms.ToTensor(),
        transforms.Normalize((0.4914,0.4822,0.4465),(0.2470,0.2435,0.2616))])
    transform_test = transforms.Compose([
        transforms.ToTensor(), transforms.Normalize((0.4914,0.4822,0.4465),(0.2470,0.2435,0.2616))])
    train_ds = HFDataset(ds['train'], transform_train)
    test_ds = HFDataset(ds['test'], transform_test)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, num_workers=4)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False, num_workers=4)
    return train_loader, test_loader

# ======================== TRAINING ========================
def evaluate(model,loader,device):
    model.eval(); correct,total=0,0
    with torch.no_grad():
        for x,y in loader: x,y=x.to(device),y.to(device); _,p=model(x).max(1); total+=y.size(0); correct+=p.eq(y).sum().item()
    return correct/total

def train_one_epoch(model,loader,opt,criterion,device):
    model.train(); total_loss,correct,total=0.0,0,0
    for x,y in loader:
        x,y=x.to(device),y.to(device); opt.zero_grad(); loss=criterion(model(x),y); loss.backward(); opt.step()
        total_loss+=loss.item()*y.size(0); _,p=model(x).max(1); total+=y.size(0); correct+=p.eq(y).sum().item()
    return total_loss/total,correct/total

def train_model(model,train_loader,test_loader,epochs,lr,device,name=''):
    criterion=nn.CrossEntropyLoss(); opt=optim.SGD(model.parameters(),lr=lr,momentum=0.9,weight_decay=5e-4)
    scheduler=optim.lr_scheduler.CosineAnnealingLR(opt,T_max=epochs)
    history={'train_loss':[],'train_acc':[],'test_acc':[],'epoch_time':[]}; best_acc=0.0
    n_params=sum(p.numel() for p in model.parameters())
    print(f'\n=== {name} | Params: {n_params:,} | Epochs: {epochs} | LR: {lr} ===')
    for epoch in range(1,epochs+1):
        t0=time.time(); train_loss,train_acc=train_one_epoch(model,train_loader,opt,criterion,device)
        test_acc=evaluate(model,test_loader,device); scheduler.step(); et=time.time()-t0
        history['train_loss'].append(train_loss); history['train_acc'].append(train_acc)
        history['test_acc'].append(test_acc); history['epoch_time'].append(et)
        if test_acc>best_acc: best_acc=test_acc; torch.save(model.state_dict(),f'output/{name}_best.pth')
        if epoch==1 or epoch%20==0 or epoch==epochs: print(f'  Epoch {epoch:3d}/{epochs} | Loss: {train_loss:.4f} | Train: {train_acc:.4f} | Test: {test_acc:.4f} | {et:.1f}s | Best: {best_acc:.4f}')
    return history,best_acc,np.mean(history['epoch_time']),n_params

def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--quick',action='store_true'); parser.add_argument('--epochs',type=int,default=80)
    args=parser.parse_args()
    if args.quick: args.epochs=3
    os.makedirs('output',exist_ok=True)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Device: {device} | GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"}')
    train_loader,test_loader=get_cifar10(batch_size=256)
    results={}
    # VGG-16
    vgg=VGG16().to(device)
    h_vgg,best_vgg,time_vgg,p_vgg=train_model(vgg,train_loader,test_loader,args.epochs,0.01,device,'VGG-16')
    results['VGG-16']={'history':h_vgg,'best_acc':best_vgg,'avg_time':time_vgg,'params':p_vgg}
    # ResNet-18
    resnet=ResNet18().to(device)
    h_rn,best_rn,time_rn,p_rn=train_model(resnet,train_loader,test_loader,args.epochs,0.05,device,'ResNet-18')
    results['ResNet-18']={'history':h_rn,'best_acc':best_rn,'avg_time':time_rn,'params':p_rn}
    # Results
    print('\n' + '='*60)
    print('  VGG-16 vs ResNet-18 FINAL RESULTS')
    print('='*60)
    print(f'  {"Metric":<20} {"VGG-16":>15} {"ResNet-18":>15}')
    print(f'  {"-"*50}')
    print(f'  {"Params":<20} {p_vgg:>15,} {p_rn:>15,}')
    print(f'  {"Best Test Acc":<20} {best_vgg:>15.4f} {best_rn:>15.4f}')
    print(f'  {"Avg Epoch Time":<20} {time_vgg:>14.1f}s {time_rn:>14.1f}s')

if __name__=='__main__': main()
