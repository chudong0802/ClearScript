
import os
import shutil
import pandas as pd
import sys
import re
import linecache
import datetime
import  glob

class Clear_Tombstone():
    def __init__(self):
        self.path = './'
        self.to_dir_path = './file/'
        self.clear_path = './tombstone/'
        self.compare_path = './compare/'
        self.compare_file = './compare/tombstone.csv'
        self.checklist_path = './tombstone_checklist.txt'
        self.dealtime = str(datetime.datetime.today()).split(" ")[0]
        self.output = 'tombstone.csv'

        if not os.path.exists(self.clear_path):
            os.mkdir(self.clear_path)
        if not os.path.exists(self.to_dir_path):
            os.mkdir(self.to_dir_path)
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

        for root,dirs,files in os.walk('./'):
            for i in range(len(files)):
                try:
                    if 'tombstone' in files[i].split('_')[0] and '.' not in files[i]:
                        if root.split('/')[1].split('\\')[0] in namelist:
                            print(str(root).split('/')[1].split('\\')[0] + ' have done')
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

            str_start = 'backtrace:'
            str_end = 'stack:'
            clist = []
            vlist = []
            tlist = []
            nlist = []
            mlist = []
            dtime = []
            dict = {'date': tlist, 'version': version, 'filename': nlist, 'module':mlist,'content': clist,'dealtime':dtime}
            used_path = []
            for xname in os.listdir(self.to_dir_path):
                final_path = os.path.join(self.to_dir_path, xname)
                if os.path.getsize(final_path) == 0:
                    # print(final_path)
                    os.remove(final_path)
                else:
                    used_path.append(final_path)
            
            if used_path != []:
                for i in range(len(used_path)):
                    module_name = []
                    file = open(used_path[i], encoding='utf-8', errors='ignore')
                    for line in file.readlines():
                        md_name = re.findall('>>>(.*?)<<<',line)
                        if len(md_name) == 0:
                            continue
                        else:
                            module_name.append(md_name)
                    file.close()
                    file = open(used_path[i], encoding='utf-8', errors='ignore')
                    content = file.read()
                    # print(content)
                    file.close()
                    #文本中包含str_start时，进行匹配
                    if str_start in content:
                        mate = re.compile(str_start + '(.*?)' + str_end, re.S)
                        result = mate.findall(content)[0]
                        result_file = open('test1.txt', 'w', encoding='utf-8')
                        result_file.write(result)
                        # 必须关掉文件，否则下一步打开的文件为空
                        result_file.close()
                    else:
                        continue
                    # 去除txt空行
                    with open('test1.txt', 'r', encoding='utf-8') as fr, open('keycontent.txt', 'w', encoding='utf-8') as fd:
                        for text in fr.readlines():
                            if text.split():
                                fd.write(text)
                    fr.close()
                    fd.close()
                    with open('keycontent.txt', 'r', encoding='utf-8') as content_file:
                        a = ''
                        for line in content_file.readlines():
                            key_content = line[29:]
                            a += key_content.strip()
                        c = a.split()
                        kcontent = ''.join(c)
                        clist.append(kcontent)
                    nlist.append(used_path[i].split('/')[-1])
                    tlist.append('/' + date)
                    vlist.append(version)
                    dtime.append(self.dealtime)
                    mlist.append(module_name[0][0])
                    content_file.close()
            else:
                continue
                
            
            dataframe = pd.DataFrame(dict)
            dataframe.to_csv('first.csv', columns=dict.keys())
            file = pd.read_csv('first.csv', index_col=0)
            frame = pd.DataFrame(file)
            frame = frame[~frame['module'].isin([' com.lerist.fakelocation',' com.yfvet.engineeringmode'])]
            # frame = frame.drop(frame[frame['module']==' com.lerist.fakelocation'].index)
            # 根据列content，再次去重
            frame.drop_duplicates(['content']) \
                .reset_index(drop=True).to_csv(self.clear_path + date + '.csv')

            with open(self.checklist_path,'a+',encoding='utf-8') as cf1:
                cf1.write(date + '\n')
            cf1.close()
            os.remove('first.csv')

            del_list = os.listdir(self.to_dir_path)
            for f in del_list:
                file_path = os.path.join(self.to_dir_path, f)
                # print(file_path)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)


    def total_file(self):

        csv_list = glob.glob('./tombstone/*.csv')
        df = pd.read_csv(csv_list[0], encoding='utf-8')
        df.to_csv(self.output, encoding='utf-8', index=False, header=True, mode='a+')
        for inputfile in csv_list[1:]:
            f = open(inputfile,encoding='utf-8')
            data = pd.read_csv(f)
            data.to_csv(self.output, mode='a+', index=False, header=False)
        print(u'合并完毕！')

        df = pd.read_csv(self.output, index_col=0, error_bad_lines=False)
        # 根据列module和content，再次去重
        datalist = df.drop_duplicates(subset=['module','content']).reset_index(drop=True)
        datalist.to_csv(self.compare_path + 'tombstone_result.csv', index=False)
        os.remove('tombstone.csv')

    
    def compare_csv(self):
        try:
            if  os.path.exists(self.compare_file):

                data = pd.read_csv(self.compare_file,encoding='utf-8')
                df1 = pd.DataFrame(data)
                new_data = pd.read_csv(self.compare_path+'tombstone_result.csv',encoding='utf-8')
                df2 = pd.DataFrame(new_data)

                num = []
                for i in range(len(df2['filename'])):
                    for j in range(len(df1['filename'])):
                        if df2['module'][i] == df1['module'][j] and df2['content'][i] == df1['content'][j]and df1['status'][j] != 'Closed':
                            num.append(i)
                        elif df2['module'][i] == df1['module'][j] and df2['content'][i] == df1['content'][j] and  df1['status'][j] != 'Resolved':
                            num.append(i)
                df2.drop([i for i in num],inplace=True)
                df2.to_csv('./compare/end_tombstone.csv',index=0)
                # print(num)
                first = pd.read_csv('./compare/tombstone.csv', encoding='utf-8')#读取第一个文件
                file1 = pd.DataFrame(first)
                end = pd.read_csv('./compare/end_tombstone.csv', encoding='utf-8')#读取第二个文件
                file2 = pd.DataFrame(end)
                outfile = pd.merge(file1,file2,how='outer')
                outfile.to_csv('./compare/{}_tombstone_result.csv'.format(self.dealtime), index=False,encoding='utf-8')#输出文件
                os.remove('./compare/end_tombstone.csv')
        except:
            pass

        
if __name__ == "__main__":
    clear_tombstone = Clear_Tombstone()
    clear_tombstone.deal_file()
    clear_tombstone.total_file()
    clear_tombstone.compare_csv()

