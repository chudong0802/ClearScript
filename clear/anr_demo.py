
import os
import shutil
import pandas as pd
import sys
import re
import linecache
import datetime
import  glob

class Clear_ANR():
    def __init__(self):
        self.path = './'
        self.to_dir_path = './file/'
        self.clear_path = './anr/'
        self.compare_path = './compare/'
        self.compare_file = './compare/anr.csv'
        self.checklist_path = './anr_checklist.txt'
        self.dealtime = str(datetime.datetime.today()).split(" ")[0]
        self.output = 'anr.csv'

        if not os.path.exists(self.clear_path):
            os.mkdir(self.clear_path)
        if not os.path.exists(self.to_dir_path):
            os.mkdir(self.to_dir_path)
        if not os.path.exists(self.compare_path):
            os.mkdir(self.compare_path)

    #清洗当前所有目录中文件名包含‘anr’的 log
    def deal_file(self):
        if not os.path.exists(self.checklist_path):
            with open(self.checklist_path,mode='w',encoding='utf-8') as f:
                pass
        namelist = []
        with open(self.checklist_path,encoding='utf-8') as cf:
            lines = cf.readlines()
            for line in lines:
                namelist.append(line.strip('\n'))
        cf.close()

        for root,dirs,files in os.walk(self.path):
            for i in range(len(files)):
                try:
                    if 'anr' in files[i].split('_')[0] and '.' not in files[i]:
                        if root.split('/')[1].split('\\')[0] in namelist:
                            print(str(root).split('/')[1].split('\\')[0] + ' have done')
                            break
                        else:
                            shutil.copy(root + '/' + files[i],self.to_dir_path)
                except:
                    pass

            used_path = []
            date = root.split('/')[1].split('\\')[0]
            for xname in os.listdir(self.to_dir_path):
                final_path = os.path.join(self.to_dir_path, xname)
                if os.path.getsize(final_path) == 0:
                    os.remove(final_path)
                else:
                    used_path.append(final_path)

            version_path = root.split('\\')[0] + '/android_ver.txt'
            if os.path.exists(version_path):
                with open(version_path,encoding='utf-8') as f:
                    version = f.read()
            else: 
                version = " "

            mlist = []
            clist = []
            vlist = []
            tlist = []
            date_list = []
            md_list = []
            used_name = []
            dtime = []
            dict = {'date': tlist, 'version': version, 'filename': used_name, 'datetime': date_list, 'module': md_list,'dealtime':dtime}
            if used_path != []:
                for j in range(len(used_path)): 
                    value_dict = {'datetime': [], 'module': []}
                    with open(used_path[j], encoding='utf-8') as f:
                    
                        for line in f.readlines():
                            if line.startswith('----- pid'):
                                value_dict['datetime'].append(re.split('at|-----', line.strip('\n'))[2])
                            elif line.startswith('Cmd'):
                                value_dict['module'].append(line.strip('\n').split(':')[1]) 
                        
                        used_name.append(used_path[j].split('/')[-1])
                        mlist.append(value_dict['datetime'])
                        date_list.append(mlist[j][0])

                        clist.append(value_dict['module'])
                        md_list.append(clist[j][0])
                        vlist.append(version)
                        tlist.append('/' + date)
                        dtime.append(self.dealtime)
            else:
                continue

            dataframe = pd.DataFrame(dict)
            dataframe.to_csv('first.csv', columns=dict.keys())
            file = pd.read_csv('first.csv', index_col=0)
            frame = pd.DataFrame(file)
            frame = frame[~frame['module'].isin([' com.lerist.fakelocation',' com.yfvet.engineeringmode'])]
            # frame = frame.drop(frame[frame['module']==' com.lerist.fakelocation'].index)
            # 根据列module和content，再次去重
            frame.drop_duplicates(subset=['datetime', 'module']) \
                .reset_index(drop=True).to_csv(self.clear_path + date + '.csv')

            with open(self.checklist_path,'a+',encoding='utf-8') as cf1:
                cf1.write(date + '\n')
            cf1.close()
            os.remove('first.csv')

            del_list = os.listdir(self.to_dir_path)
            for f in del_list:
                file_path = os.path.join(self.to_dir_path, f)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

    
    def total_file(self):
        csv_list = glob.glob('./anr/*.csv')
        print(csv_list)
        df = pd.read_csv(csv_list[0], encoding='utf-8')
        df.to_csv(self.output, encoding='utf-8', index=False, header=True, mode='a+')
        for inputfile in csv_list[1:]:
            f = open(inputfile,encoding='utf-8')
            data = pd.read_csv(f)
            data.to_csv(self.output, mode='a+', index=False, header=False)
        print(u'All files have been merged')
        df = pd.read_csv(self.output, index_col=0, error_bad_lines=False)
        # 根据列module和content，再次去重
        datalist = df.drop_duplicates(subset=['module','datetime']).reset_index(drop=True)
        datalist.to_csv(self.compare_path + 'anr_result.csv', index=False)
        os.remove('anr.csv')
        
    def compare_csv(self):
        try:
            if  os.path.exists(self.compare_file):
                data = pd.read_csv(self.compare_file)
                df1 = pd.DataFrame(data)
                new_data = pd.read_csv(self.compare_path+'anr_result.csv')
                df2 = pd.DataFrame(new_data)

                num = []
                for i in range(len(df2['filename'])):
                    for j in range(len(df1['filename'])):
                        if df2['module'][i] == df1['module'][j] and df2['datetime'][i] == df1['datetime'][j]and df1['status'][j] != 'Closed':
                            num.append(i)
                        elif df2['module'][i] == df1['module'][j] and df2['datetime'][i] == df1['datetime'][j] and  df1['status'][j] != 'Resolved':
                            num.append(i)
                print(num)
                df2.drop([i for i in num],inplace=True)
                df2.to_csv('./compare/end_anr.csv',index=0)

                first = pd.read_csv('./compare/anr.csv')#读取第一个文件
                file1 = pd.DataFrame(first)
                # print(file1)
                end = pd.read_csv('./compare/end_anr.csv')#读取第二个文件
                file2 = pd.DataFrame(end)
                outfile = pd.merge(file1,file2,how='outer')
                outfile.to_csv('./compare/{}_anr_result.csv'.format(self.dealtime), index=False)#输出文件
                os.remove('./compare/end_anr.csv')
        except:
            pass

        
if __name__ == "__main__":
    clear_anr = Clear_ANR()
    clear_anr.deal_file()
    clear_anr.total_file()
    clear_anr.compare_csv()

