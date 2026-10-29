import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="河北省手枪项目科技工作数据平台",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.title("🎯 河北省手枪项目科技工作数据平台")
st.markdown("> 围绕生理机能、功能评估、体能训练、专项训练、营养伤病实现一体化监测管理")

if "athlete_list" not in st.session_state:
    st.session_state.athlete_list = pd.DataFrame(columns=[
        "athlete_id", "name", "gender", "event", "train_years", "remark"
    ])
if "data_hrv" not in st.session_state:
    st.session_state.data_hrv = pd.DataFrame(columns=[
        "athlete_id", "test_date", "HF", "LF_HF", "RMSSD", "remark"
    ])
if "data_cff" not in st.session_state:
    st.session_state.data_cff = pd.DataFrame(columns=[
        "athlete_id", "test_date", "CFF", "remark"
    ])
if "data_blood" not in st.session_state:
    st.session_state.data_blood = pd.DataFrame(columns=[
        "athlete_id", "test_date", "T", "C", "T_C", "BUN", "Hb", "CK", "remark"
    ])
if "data_shoulder" not in st.session_state:
    st.session_state.data_shoulder = pd.DataFrame(columns=[
        "athlete_id", "test_date",
        "rot_ext_N", "rot_in_N", "rot_ratio", "asym_rate",
        "serratus_N", "serratus_endurance", "winging_level",
        "shake_amp", "shake_cv", "remark"
    ])
if "data_training" not in st.session_state:
    st.session_state.data_training = pd.DataFrame(columns=[
        "athlete_id", "train_date", "train_type", "content", "load_info", "subject_feel", "remark"
    ])
if "data_nurse" not in st.session_state:
    st.session_state.data_nurse = pd.DataFrame(columns=[
        "athlete_id", "record_date", "type", "content", "plan", "status"
    ])

menu = st.sidebar.selectbox(
    "📋 功能导航",
    ["运动员档案管理",
     "生理机能监控录入",
     "肩胛&持枪稳定评估录入",
     "训练记录录入",
     "营养伤病录入",
     "数据可视化分析",
     "数据导出"]
)

if menu == "运动员档案管理":
    st.subheader("运动员基础档案")
    col1, col2 = st.columns(2)
    with col1:
        aid = st.text_input("运动员编号")
        aname = st.text_input("姓名")
        agender = st.selectbox("性别", ["男", "女"])
        aevent = st.selectbox("专项", ["10米气手枪", "25米手枪", "速射手枪"])
        aty = st.number_input("训练年限", min_value=0, max_value=30, value=2)
        aremark = st.text_area("备注")
        if st.button("新增/更新档案"):
            new_row = pd.DataFrame([{
                "athlete_id": aid, "name": aname, "gender": agender,
                "event": aevent, "train_years": aty, "remark": aremark
            }])
            st.session_state.athlete_list = pd.concat([
                st.session_state.athlete_list[st.session_state.athlete_list["athlete_id"] != aid],
                new_row
            ], ignore_index=True)
            st.success("✅ 档案保存成功！")
    with col2:
        st.dataframe(st.session_state.athlete_list, use_container_width=True)
        if not st.session_state.athlete_list.empty:
            del_id = st.selectbox("选择要删除的运动员编号", st.session_state.athlete_list["athlete_id"].unique())
            if st.button("删除该运动员档案"):
                st.session_state.athlete_list = st.session_state.athlete_list[st.session_state.athlete_list["athlete_id"] != del_id]
                st.warning("已删除")

elif menu == "生理机能监控录入":
    st.subheader("生理机能状态监控（HRV / CFF / 血液生化）")
    tab1, tab2, tab3 = st.tabs(["HRV自主神经", "CFF闪光融合", "阶段血液生化"])
    athlete_ids = st.session_state.athlete_list["athlete_id"].unique().tolist()
    if len(athlete_ids) == 0:
        st.info("请先录入运动员档案")
    else:
        with tab1:
            sel_id = st.selectbox("选择运动员", athlete_ids, key="hrv_id")
            tdate = st.date_input("测试日期", value=datetime.now())
            hf = st.number_input("HF", value=0.0)
            lfhf = st.number_input("LF/HF", value=0.0)
            rmssd = st.number_input("RMSSD", value=0.0)
            rem = st.text_input("备注（疲劳、体感）")
            if st.button("保存HRV记录"):
                nr = pd.DataFrame([{
                    "athlete_id": sel_id, "test_date": tdate,
                    "HF": hf, "LF_HF": lfhf, "RMSSD": rmssd, "remark": rem
                }])
                st.session_state.data_hrv = pd.concat([st.session_state.data_hrv, nr], ignore_index=True)
                st.success("HRV数据已录入")
            st.dataframe(st.session_state.data_hrv.tail(8))

        with tab2:
            sel_id = st.selectbox("选择运动员", athlete_ids, key="cff_id")
            tdate = st.date_input("测试日期", value=datetime.now(), key="cff_dt")
            cff_val = st.number_input("CFF闪光融合频率值", value=0.0)
            rem = st.text_input("备注", key="cff_rem")
            if st.button("保存CFF记录"):
                nr = pd.DataFrame([{
                    "athlete_id": sel_id, "test_date": tdate, "CFF": cff_val, "remark": rem
                }])
                st.session_state.data_cff = pd.concat([st.session_state.data_cff, nr], ignore_index=True)
                st.success("CFF数据已录入")
            st.dataframe(st.session_state.data_cff.tail(8))

        with tab3:
            sel_id = st.selectbox("选择运动员", athlete_ids, key="blood_id")
            tdate = st.date_input("采血日期", value=datetime.now())
            t = st.number_input("睾酮 T", value=0.0)
            c = st.number_input("皮质醇 C", value=0.0)
            tc = st.number_input("T/C比值", value=0.0)
            bun = st.number_input("BUN血尿素", value=0.0)
            hb = st.number_input("Hb血红蛋白", value=0.0)
            ck = st.number_input("CK肌酸激酶", value=0.0)
            rem = st.text_input("生化备注")
            if st.button("保存生化记录"):
                nr = pd.DataFrame([{
                    "athlete_id": sel_id, "test_date": tdate,
                    "T": t, "C": c, "T_C": tc, "BUN": bun, "Hb": hb, "CK": ck, "remark": rem
                }])
                st.session_state.data_blood = pd.concat([st.session_state.data_blood, nr], ignore_index=True)
                st.success("生化数据已录入")
            st.dataframe(st.session_state.data_blood.tail(6))

elif menu == "肩胛&持枪稳定评估录入":
    st.subheader("🔍 肩袖肌力、前锯肌、持枪稳定性评估（MicroFET3+陀螺仪）")
    athlete_ids = st.session_state.athlete_list["athlete_id"].unique().tolist()
    if len(athlete_ids) == 0:
        st.info("请先录入运动员档案")
    else:
        sel_id = st.selectbox("选择运动员", athlete_ids)
        tdate = st.date_input("评估日期", value=datetime.now())
        col1, col2, col3 = st.columns(3)
        with col1:
            rot_ext = st.number_input("肩袖外旋肌力 N", value=0.0)
            rot_in = st.number_input("肩袖内旋肌力 N", value=0.0)
            rot_ratio = st.number_input("旋外/旋内比值", value=0.0, help="正常区间0.6~0.8")
            asym = st.number_input("双侧不对称率 %", value=0.0)
        with col2:
            serratus_n = st.number_input("前锯肌等长肌力 N", value=0.0)
            serratus_end = st.number_input("推墙耐力次数", value=0)
            wing_lv = st.selectbox("翼状肩胛分级", ["无", "轻度", "中度", "重度"])
        with col3:
            shake_amp = st.number_input("枪口晃动幅度", value=0.0)
            shake_cv = st.number_input("晃动变异系数", value=0.0)
            rem = st.text_input("评估备注")
        if st.button("保存本次功能评估"):
            nr = pd.DataFrame([{
                "athlete_id": sel_id, "test_date": tdate,
                "rot_ext_N": rot_ext, "rot_in_N": rot_in, "rot_ratio": rot_ratio, "asym_rate": asym,
                "serratus_N": serratus_n, "serratus_endurance": serratus_end, "winging_level": wing_lv,
                "shake_amp": shake_amp, "shake_cv": shake_cv, "remark": rem
            }])
            st.session_state.data_shoulder = pd.concat([st.session_state.data_shoulder, nr], ignore_index=True)
            st.success("✅ 肩胛与持枪稳定评估已保存")
        st.dataframe(st.session_state.data_shoulder.tail(8), use_container_width=True)

elif menu == "训练记录录入":
    st.subheader("📝 功能性训练 / 专项体能 / 手枪专项训练记录")
    athlete_ids = st.session_state.athlete_list["athlete_id"].unique().tolist()
    if len(athlete_ids) == 0:
        st.info("请先录入运动员档案")
    else:
        sel_id = st.selectbox("选择运动员", athlete_ids)
        tdate = st.date_input("训练日期", value=datetime.now())
        train_type = st.selectbox("训练类型", [
            "静力慢速力量（枪架）",
            "核心抗旋训练（枪托）",
            "肩关节功能训练（准星）",
            "专项供能整合训练",
            "实弹专项训练",
            "模拟瞄准训练"
        ])
        content = st.text_area("训练内容简述")
        load = st.text_input("负荷信息（组数、次数、负重）")
        feel = st.selectbox("运动员主观感受", ["良好", "轻微疲劳", "疲劳明显", "疼痛不适"])
        rem = st.text_input("备注")
        if st.button("保存训练记录"):
            nr = pd.DataFrame([{
                "athlete_id": sel_id, "train_date": tdate,
                "train_type": train_type, "content": content, "load_info": load,
                "subject_feel": feel, "remark": rem
            }])
            st.session_state.data_training = pd.concat([st.session_state.data_training, nr], ignore_index=True)
            st.success("训练记录保存成功")
        st.dataframe(st.session_state.data_training.tail(8))

elif menu == "营养伤病录入":
    st.subheader("🩺 营养管理 & 伤病监测记录")
    athlete_ids = st.session_state.athlete_list["athlete_id"].unique().tolist()
    if len(athlete_ids) == 0:
        st.info("请先录入运动员档案")
    else:
        sel_id = st.selectbox("选择运动员", athlete_ids)
        rdate = st.date_input("记录日期", value=datetime.now())
        rec_type = st.selectbox("记录类别", ["营养膳食", "肩袖损伤", "肩峰撞击", "斜方肌劳损", "前臂劳损", "颈肩不适", "其他伤病"])
        content = st.text_area("详细情况描述")
        plan = st.text_area("干预方案（营养补给/康复）")
        status = st.selectbox("当前状态", ["新发", "康复中", "已恢复"])
        if st.button("保存营养伤病记录"):
            nr = pd.DataFrame([{
                "athlete_id": sel_id, "record_date": rdate,
                "type": rec_type, "content": content, "plan": plan, "status": status
            }])
            st.session_state.data_nurse = pd.concat([st.session_state.data_nurse, nr], ignore_index=True)
            st.success("记录已保存")
        st.dataframe(st.session_state.data_nurse.tail(8))

elif menu == "数据可视化分析":
    st.subheader("📊 数据趋势分析与联动查看")
    athlete_ids = st.session_state.athlete_list["athlete_id"].unique().tolist()
    if len(athlete_ids) == 0:
        st.info("暂无运动员数据")
    else:
        sel_id = st.selectbox("选择运动员查看趋势", athlete_ids)
        tab1, tab2, tab3, tab4 = st.tabs(["HRV趋势", "CFF趋势", "肩袖比值&晃动", "生化T/C"])
        with tab1:
            dfh = st.session_state.data_hrv[st.session_state.data_hrv["athlete_id"] == sel_id].copy()
            if not dfh.empty:
                dfh["test_date"] = pd.to_datetime(dfh["test_date"])
                fig = px.line(dfh, x="test_date", y=["RMSSD", "HF", "LF_HF"], title="自主神经指标趋势")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无HRV数据")
        with tab2:
            dfc = st.session_state.data_cff[st.session_state.data_cff["athlete_id"] == sel_id].copy()
            if not dfc.empty:
                dfc["test_date"] = pd.to_datetime(dfc["test_date"])
                fig = px.line(dfc, x="test_date", y="CFF", title="CFF中枢疲劳趋势")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无CFF数据")
        with tab3:
            dfs = st.session_state.data_shoulder[st.session_state.data_shoulder["athlete_id"] == sel_id].copy()
            if not dfs.empty:
                dfs["test_date"] = pd.to_datetime(dfs["test_date"])
                fig1 = px.line(dfs, x="test_date", y="rot_ratio", title="肩袖旋外/旋内比值（正常0.6~0.8）")
                fig1.add_hline(y=0.6, line_dash="dash", line_color="red")
                fig1.add_hline(y=0.8, line_dash="dash", line_color="green")
                st.plotly_chart(fig1, use_container_width=True)
                fig2 = px.line(dfs, x="test_date", y=["shake_amp", "shake_cv"], title="枪口晃动指标变化")
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("暂无肩胛与持枪稳定评估数据")
        with tab4:
            dfb = st.session_state.data_blood[st.session_state.data_blood["athlete_id"] == sel_id].copy()
            if not dfb.empty:
                dfb["test_date"] = pd.to_datetime(dfb["test_date"])
                fig = px.line(dfb, x="test_date", y=["T_C", "Hb", "CK"], title="生化指标趋势")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无生化数据")

elif menu == "数据导出":
    st.subheader("💾 批量导出全部数据表（Excel）")
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        st.session_state.athlete_list.to_excel(writer, sheet_name="运动员档案", index=False)
        st.session_state.data_hrv.to_excel(writer, sheet_name="HRV数据", index=False)
        st.session_state.data_cff.to_excel(writer, sheet_name="CFF数据", index=False)
        st.session_state.data_blood.to_excel(writer, sheet_name="血液生化", index=False)
        st.session_state.data_shoulder.to_excel(writer, sheet_name="肩胛持枪评估", index=False)
        st.session_state.data_training.to_excel(writer, sheet_name="训练记录", index=False)
        st.session_state.data_nurse.to_excel(writer, sheet_name="营养伤病", index=False)
    output.seek(0)
    st.download_button(
        label="📥 下载全部数据Excel",
        data=output,
        file_name="河北省手枪项目科技平台数据.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    st.markdown("导出包含7张工作表，可离线备份、统计分析、队内归档")
