import plotly.express as px
import streamlit as st

from nl_query import ask, build_schema_context

st.set_page_config(page_title="Football Intelligence", layout="wide")


@st.cache_resource
def get_schema():
    return build_schema_context()


def infer_chart(df):
    """Pick a chart from the shape of the result. Returns (kind, x, y) or None."""
    if df.empty or len(df) < 2:
        return None

    num = df.select_dtypes("number").columns.tolist()
    cat = df.select_dtypes(include=["object", "string", "bool"]).columns.tolist()

    for t in ("gw", "season", "made_at_gw"):
        if t in df.columns and num:
            y = next((c for c in num if c != t), None)
            if y:
                return "line", t, y

    if len(cat) >= 1 and len(num) >= 1:
        if len(num) >= 2 and len(df) > 10:
            return "scatter", num[0], num[1]
        return "bar", cat[0], num[0]

    if len(num) >= 2:
        return "scatter", num[0], num[1]

    return None


st.title("Football Intelligence")
st.caption("Ask questions about FPL, Understat and FBref data in plain English.")


schema = get_schema()

question = st.text_input(
    "Question",
    placeholder="Who are the best value midfielders under £6m?",
)

if question:
    with st.spinner("Thinking..."):
        result = ask(question, schema=schema, verbose=False)

    if "error" in result:
        st.error(result["error"])
        if result.get("sql"):
            with st.expander("Generated SQL"):
                st.code(result["sql"], language="sql")

    else:
        df = result["data"]

        st.caption(f"{result['rows']} rows")

        chart = infer_chart(df)
        if chart:
            kind, x, y = chart
            fig = {
                "bar": lambda: px.bar(df, x=x, y=y),
                "line": lambda: px.line(df, x=x, y=y, markers=True),
                "scatter": lambda: px.scatter(
                    df,
                    x=x,
                    y=y,
                    hover_data=[c for c in df.columns if c not in (x, y)][:3],
                ),
            }[kind]()
            fig.update_layout(height=420, margin=dict(t=30, b=30))
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df, use_container_width=True)

        with st.expander("Generated SQl"):
            st.code(result["sql"], language="sql")
