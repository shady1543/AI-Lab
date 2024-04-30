## 分类

### 信誉度分类任务

`DT_data.csv`数据集包含三列共600条数据，其中每条数据有如下属性：

* Undergrad : person is under graduated or not
* MaritalStatus : marital status of a person
* TaxableIncome : Taxable income is the amount of how much tax an individual owes to the government 
* WorkExperience : Work experience of an individual person
* Urban : Whether that person belongs to urban area or not

将那些 `TaxableIncome <= 30000` 的人视为”有风险”，而其他人则为“好”。利用决策树算法实现对个人信誉度的分类。

### 提示

1. 最后提交的代码只需包含性能最好的实现方法和参数设置. 只需提交一个代码文件, 请不要提交其他文件.
2. 本次作业可以使用 `numpy`库、`matplotlib`库以及python标准库.
3. 数据集可以在Github上下载。
