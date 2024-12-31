from phi.agent import Agent
from phi.model.google import Gemini
import streamlit as st
from PIL import Image
from typing import List, Optional
from streamlit_paste_button import paste_image_button as pbutton
import uuid
import io


def initialize_agents(api_key: str) -> tuple[Agent, Agent, Agent]:
    try:
        model = Gemini(id="gemini-2.0-flash-exp", api_key=api_key)

        vision_agent = Agent(
            model=model,
            instructions=[
                "You are a visual analysis expert that:",
                "1. Identifies design elements, patterns, and visual hierarchy",
                "2. Analyzes color schemes, typography, and layouts",
                "3. Detects UI components and their relationships",
                "4. Evaluates visual consistency and branding",
                "Be specific and technical in your analysis"
            ],
            markdown=True
        )

        ux_agent = Agent(
            model=model,
            instructions=[
                "You are a UX analysis expert that:",
                "1. Evaluates user flows and interaction patterns",
                "2. Identifies usability issues and opportunities",
                "3. Suggests UX improvements based on best practices",
                "4. Analyzes accessibility and inclusive design",
                "Focus on user-centric insights and practical improvements"
            ],
            markdown=True
        )

        return vision_agent, ux_agent
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None, None, None


# Sidebar for API key input
with st.sidebar:
    st.header("🔑 API Configuration")

    if "api_key_input" not in st.session_state:
        st.session_state.api_key_input = ""

    api_key = st.text_input(
        "Enter your Gemini API Key",
        value=st.session_state.api_key_input,
        type="password",
        help="Get your API key from Google AI Studio",
        key="api_key_widget"
    )

    if api_key != st.session_state.api_key_input:
        st.session_state.api_key_input = api_key

    if api_key:
        st.success("API Key provided! ✅")
    else:
        st.warning("Please enter your API key to proceed")
        st.markdown("""
        To get your API key:
        1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
        """)

st.header("Multimodal AI Design Agent Team")


if st.session_state.api_key_input:
    vision_agent, ux_agent = initialize_agents(
        st.session_state.api_key_input)

    if all([vision_agent, ux_agent]):
        # File Upload Section
        st.subheader("📤 Upload Design")

        design_files = []

        paste_image = pbutton("📋 Paste an Image",
                              text_color="#ffffff",
                              background_color="#007BFF",
                              hover_background_color="#016FE6")
        if paste_image.image_data is not None:
            st.image(paste_image.image_data)
            design_files.append(paste_image)

        # Analysis Configuration
        st.subheader("🎯 Configuration")

        analysis_types = st.multiselect(
            "Select Analysis Types",
            ["Visual Design", "User Experience"],
            default=["User Experience"]
        )

        specific_elements = st.multiselect(
            "Focus Areas",
            ["Color Scheme", "Typography", "Layout", "Navigation",
             "Interactions", "Accessibility"],
            default=["Interactions"]
        )

        context = st.text_area(
            "Additional Context",
            placeholder="Describe your product, target audience, or specific concerns..."
        )

        # Analysis Process
        if st.button("🚀 Run Analysis", type="primary"):
            print(len(design_files))
            if design_files:
                try:
                    # Process images once
                    def process_images(files):
                        processed_images = []
                        for file in files:
                            try:
                                # Create a temporary file path for the image
                                import tempfile
                                import os

                                temp_dir = tempfile.gettempdir()

                                temp_path = os.path.join(
                                    temp_dir, f"{uuid.uuid4().hex}.png")

                                img_bytes = io.BytesIO()
                                file.image_data.save(img_bytes, format="PNG")
                                with open(temp_path, "wb") as f:
                                    f.write(img_bytes.getvalue())

                                # Add the path to processed images
                                processed_images.append(temp_path)

                            except Exception as e:
                                st.error(
                                    f"Error processing image {file.name}: {str(e)}")
                                continue
                        return processed_images

                    image_urls = process_images(design_files)

                    # Visual Design Analysis
                    if "Visual Design" in analysis_types and design_files:
                        with st.spinner("🎨 Analyzing visual design..."):
                            if image_urls:
                                vision_prompt = f"""
                                Analyze these designs focusing on: {', '.join(specific_elements)}
                                Additional context: {context}
                                Provide specific insights about visual design elements.

                                Please format your response with clear headers and bullet points.
                                Focus on concrete observations and actionable insights.
                                """

                                response = vision_agent.run(
                                    message=vision_prompt,
                                    images=image_urls
                                )

                                st.subheader("🎨 Visual Design Analysis")
                                st.markdown(response.content)

                    # UX Analysis
                    if "User Experience" in analysis_types:
                        with st.spinner("🔄 Analyzing user experience..."):
                            if image_urls:
                                ux_prompt = f"""
                                Evaluate the user experience considering: {', '.join(specific_elements)}
                                Additional context: {context}
                                Focus on user flows, interactions, and accessibility.

                                Please format your response with clear headers and bullet points.
                                Focus on concrete observations and actionable improvements.
                                """

                                response = ux_agent.run(
                                    message=ux_prompt,
                                    images=image_urls
                                )

                                st.subheader("🔄 UX Analysis")
                                st.markdown(response.content)

                    # Combined Insights
                    if len(analysis_types) > 1:
                        st.subheader("🎯 Key Takeaways")
                        st.info("""
                        Above you'll find detailed analysis from multiple specialized AI agents, each focusing on their area of expertise:
                        - Visual Design Agent: Analyzes design elements and patterns
                        - UX Agent: Evaluates user experience and interactions
                        """)

                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
                    st.error("Please check your API key and try again.")
            else:
                st.warning("Please upload at least one design to analyze.")
    else:
        st.info("👈 Please enter your API key in the sidebar to get started")
else:
    st.info("👈 Please enter your API key in the sidebar to get started")

# Footer with usage tips
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <h4>Tips for Best Results</h4>
    <p>
    • Upload clear, high-resolution images<br>
    • Provide specific context about your target audience
    </p>
</div>
""", unsafe_allow_html=True)
