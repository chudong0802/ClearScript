
import os
import shutil
import pandas as pd
import sys
import re
import linecache
import datetime
import  glob

class Clear_STRICTMODE():
    def __init__(self):
        self.path = './'
        self.to_dir_path = './file/'
        self.end_dir_path = './newfile/'
        self.clear_path = './strictmode/'
        self.compare_path = './compare/'
        self.compare_file = './compare/strictmode.csv'
        self.checklist_path = './strictmode_checklist.txt'
        self.dealtime = str(datetime.datetime.today()).split(" ")[0]
        self.output = 'strictmode.csv'

        if not os.path.exists(self.clear_path):
            os.mkdir(self.clear_path)
        if not os.path.exists(self.to_dir_path):
            os.mkdir(self.to_dir_path)
        if not os.path.exists(self.end_dir_path):
            os.mkdir(self.end_dir_path)
        if not os.path.exists(self.compare_path):
            os.mkdir(self.compare_path)
    
    #清洗当前所有目录中文件名包含‘app_crash’的 log
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
                    if 'app_strictmode' in files[i].split('.')[0] and files[i].split('.')[-1]=='txt':
                        if root.split('/')[1].split('\\')[0] in namelist:
                            print(root.split('/')[1].split('\\')[0] + ' have done')
                            break
                        else:
                            shutil.copy(root + '/' + files[i],self.to_dir_path)
                except:
                    pass

            version_path = root.split('\\')[0] + '/android_ver.txt'
            if os.path.exists(version_path):
                with open(version_path,encoding='utf-8') as f:
                    version = f.read()
            else:
                version = " "

            date = root.split('/')[1].split('\\')[0]
            new_namelist = []
            for root, dir, files in os.walk(self.to_dir_path):
                for file1 in files:
                    if os.path.splitext(file1)[1] == '.txt':
                        new_namelist.append(os.path.splitext(file1)[0])
            txt_path = []
            for name in os.listdir(self.to_dir_path):
                tpath = os.path.join(self.to_dir_path, name)
                if os.path.getsize(self.to_dir_path) == 0:
                    os.remove(tpath)
                else:
                    txt_path.append(tpath)

            for i in range(len(txt_path)):
                writePath = self.end_dir_path + new_namelist[i]
                lines_seen = set()
                outfiile = open(writePath, 'a+', encoding='utf-8')
                f = open(txt_path[i], 'r', encoding='utf-8')
                for line in f:
                    if line not in lines_seen:
                        outfiile.write(line)
                        lines_seen.add(line)
                f.close()
                outfiile.close()
            used_path = []
            for xname in os.listdir(self.end_dir_path):
                final_path = os.path.join(self.end_dir_path, xname)
                used_path.append(final_path)

            mlist = []
            clist = []
            vlist = []
            tlist = []
            dtime = []
            dict = {'date': tlist, 'version': version, 'filename': new_namelist, 'module': mlist, 'content': clist,'dealtime':dtime}
            if used_path != []:
                for j in range(len(new_namelist)):
                    value_dict = {'Process': [], 'key': []}
                    with open(used_path[j], encoding='utf-8') as uf:
                        for line in uf.readlines():
                            if line.startswith('Process'):
                                value_dict['Process'].append(line.strip('\n').split(':')[1])
                            elif line.startswith('android') or line.startswith('java'):
                                value_dict['key'].append(line.strip('\n'))
                        # print(value_dict['Process'])
                        # print(value_dict)
                        mlist.append(value_dict['Process'])
                        clist.append(value_dict['key'])
                        vlist.append(version)
                        tlist.append('/' + date)
                        dtime.append(self.dealtime)
                    uf.close()
            else:
                continue

            dataframe = pd.DataFrame(dict)
            dataframe.to_csv('first.csv', columns=dict.keys())
            file = pd.read_csv('first.csv', index_col=0)
            frame = pd.DataFrame(file)
            frame = frame[~frame['module'].isin([' com.lerist.fakelocation',' com.yfvet.engineeringmode'])]
            # frame = frame.drop(frame[frame['module']==' com.lerist.fakelocation'].index)
            # 根据列module和content，再次去重
            frame.drop_duplicates(subset=['module', 'content']) \
                .reset_index(drop=True).to_csv(self.clear_path + date + '.csv')

            with open(self.checklist_path,'a+',encoding='utf-8') as cf1:
                cf1.write(date + '\n')
            cf1.close()
            os.remove('first.csv')

            """
            删除某一目录下的所有文件或文件夹
            :param filepath: 路径
            :return:
            """
            del_list = os.listdir(self.to_dir_path)
            for df in del_list:
                file_path = os.path.join(self.to_dir_path, df)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

            del_list1 = os.listdir(self.end_dir_path)
            for f1 in del_list1:
                file_path1 = os.path.join(self.end_dir_path, f1)
                if os.path.isfile(file_path1):
                    os.remove(file_path1)
                elif os.path.isdir(file_path1):
                    shutil.rmtree(file_path1)


    def total_file(self):
        csv_list = glob.glob('./strictmode/*.csv')
        df = pd.read_csv(csv_list[0], encoding='utf-8',engine='python')
        df.to_csv(self.output, encoding='utf-8', index=False, header=True, mode='a+')
        for inputfile in csv_list[1:]:
            f = open(inputfile,encoding='utf-8')
            data = pd.read_csv(f)
            data.to_csv(self.output, mode='a+', index=False, header=False)
        print(u'合并完毕！')
        df = pd.read_csv(self.output, index_col=0, error_bad_lines=False)
        # 根据列module和content，再次去重
        datalist = df.drop_duplicates(subset=['module','content']).reset_index(drop=True)
        datalist.to_csv(self.compare_path + 'strictmode_result.csv', index=False)
        os.remove('strictmode.csv')

    
    def compare_csv(self):
        try:
            if  os.path.exists(self.compare_file):

                data = pd.read_csv(self.compare_file,encoding='utf-8')
                df1 = pd.DataFrame(data)
                new_data = pd.read_csv(self.compare_path+'strictmode_result.csv',encoding='utf-8')
                df2 = pd.DataFrame(new_data)

                num = []
                for i in range(len(df2['filename'])):
                    for j in range(len(df1['filename'])):
                        if df2['module'][i] == df1['module'][j] and df2['content'][i] == df1['content'][j]and df1['status'][j] != 'Closed':
                            num.append(i)
                        elif df2['module'][i] == df1['module'][j] and df2['content'][i] == df1['content'][j] and  df1['status'][j] != 'Resolved':
                            num.append(i)
                df2.drop([i for i in num],inplace=True)
                df2.to_csv('./compare/end_strictmode.csv',index=0)
                # print(num)

                first = pd.read_csv('./compare/strictmode.csv', encoding='utf-8')#读取第一个文件
                file1 = pd.DataFrame(first)
                # print(file1)
                end = pd.read_csv('./compare/end_strictmode.csv', encoding='utf-8')#读取第二个文件
                file2 = pd.DataFrame(end)
                outfile = pd.merge(file1,file2,how='outer')
                outfile.to_csv('./compare/{}_strictmode_result.csv'.format(self.dealtime), index=False,encoding='utf-8')#输出文件
                os.remove('./compare/end_strictmode.csv')
        except:
            pass

        
if __name__ == "__main__":
    clear_strictmode = Clear_STRICTMODE()
    clear_strictmode.deal_file()
    clear_strictmode.total_file()
    clear_strictmode.compare_csv()

