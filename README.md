### SignFlow: Live ASL Interpretation & Learning

Convert speech to ASL with 3D signing and display a virtual ASL interpreter using a virtual camera for seamless online meetings. Practice fingerspelling with real-time ASL alphabet recognition.

### YouTube  
[Watch the video](https://www.youtube.com/watch?v=284L0caFRUI&t=132s)

### **Inspiration**

At Duke University’s 100th-anniversary celebration, a live ASL interpreter translated the event in real time. Watching the expressive motions of sign language, we realized how much more engaging and natural it felt compared to plain captions or text. For Deaf individuals, these dynamic gestures create a sense of connection, inclusion, and belonging that words alone cannot achieve.

However, having professional interpreters at every event, meeting, or conversation comes with significant logistical and financial challenges. We envisioned a solution that could bridge this gap—offering real-time speech-to-sign translation to make communication more seamless and accessible on a broader scale.

Beyond accessibility, we also wanted to encourage more people to learn ASL. By integrating fingerspelling recognition, our platform helps beginners practice and refine their gestures, fostering greater interest in sign language and deeper awareness of the Deaf community. Our goal is not just to build technology, but to build a world where communication knows no barriers.

### **What it does**

**SignFlow** is an AI-powered ASL translation and learning platform designed to enhance accessibility and inclusion. It provides:

- **Real-time speech-to-ASL translation**, converting spoken words into dynamic 3D sign animations for a more engaging and natural communication experience.
- **Virtual ASL interpreter overlay**, allowing users to stream a signing avatar into online meetings via a virtual camera.
- **AI-driven fingerspelling recognition**, helping beginners practice and refine ASL alphabet gestures with instant feedback.
- **Scalable accessibility solutions**, making ASL interpretation more widely available without the high cost of human interpreters.

### **How We Built It**

**SignFlow** was developed using AI-powered models and 3D animation techniques to create a seamless ASL interpretation experience. It includes:

- **Speech-to-text conversion** using **whisper ASR (Automatic Speech Recognition)** for accurate and real-time transcription of spoken words. This text is then processed to generate ASL animations.
- **Pose and hand tracking** with **MediaPipe’s Pose and Hand Landmark Models**, extracting body keypoints from video frames for accurate ASL animations.
- **Speech-to-ASL translation** powered by the **all-MiniLM-L6-v2 model**, which converts transcribed text into embeddings to determine corresponding ASL signs.
- **Database storage and retrieval** using **PostgreSQL with pgvector**, storing words, embeddings, and ASL sign point animations for fast access.
- **3D animated signing avatar** built with **Three.js and React Three Fiber**, rendering expressive hand and body movements based on processed text.
- **Dynamic hand pose visualization** implemented using **Three.js SphereGeometry and TubeGeometry**, simulating hand and arm movements for smooth signing transitions.
- **Real-time fingerspelling detection** using **TensorFlow.js and webcam integration**, capturing hand signs and mapping them to ASL letters.
- **Socket-based communication** with **Socket.io**, enabling fast, interactive animation updates from speech input.
- **Virtual ASL interpreter overlay** using **WebRTC and a virtual camera setup**, allowing users to display an AI-driven interpreter in online meetings.

By integrating **AI, 3D rendering, and real-time communication**, we created a powerful tool for accessibility and ASL learning.

### **Challenges We Ran Into**

1. **Inconsistent ASL Video Sources** – Our initial approach was to map each spoken word to a corresponding ASL video. However, since the videos came from different sources, they lacked uniformity, making transitions between signs appear unnatural.
2. **Keypoint-Based ASL Representation** – To address this, we extracted **keypoints from ASL videos** using **MediaPipe’s Pose and Hand Landmark Models** instead of relying on raw videos. However, obtaining a large, high-quality dataset was challenging. Ultimately, we built a database containing approximately **2,000 words with their corresponding ASL sign animations**.
3. **Strict Hand Gesture Requirements for Fingerspelling** – Due to time constraints, our **real-time fingerspelling recognition** required precise hand positioning, making it more demanding for beginners. This highlighted the need for future improvements in gesture flexibility and robustness.

### **Accomplishments That We're Proud Of**

1. **Real-time Speech-to-ASL Translation** – Our system accurately converts spoken words into **fluid ASL animations**, even handling full phrases like *“Happy wife, happy life”* naturally.
2. **3D Animated Signing Avatar** – Built with **Three.js and React Three Fiber**, our avatar performs smooth, expressive ASL gestures.
3. **Efficient ASL Keypoint Storage** – We processed **2,000+ words** using **MediaPipe’s Pose and Hand Landmark Models** and stored animations in **PostgreSQL + pgvector** for fast retrieval.
4. **Real-time Fingerspelling Recognition** – AI-driven hand tracking allows users to **practice ASL fingerspelling** with instant feedback.
5. **Virtual ASL Interpreter & Scalable Design** – With **WebRTC and a virtual camera**, users can overlay an **AI-powered ASL interpreter** into video calls. Our modular system supports **future expansions** like more signs, better gesture recognition.

### **What We Learned**

1. **ASL is more than words** – We had to rethink translation since **ASL isn’t word-for-word English** but a rich, expressive language.
2. **Good ASL data is hard to find** – Collecting **consistent, high-quality signing data** was a challenge, so we extracted keypoints using **MediaPipe** to standardize animations.
3. **Making 3D signing smooth is tricky** – Balancing **realism and performance** in our **Three.js avatar** took a lot of fine-tuning.

### **What's Next for SignFlow**

1. **Expanding ASL Vocabulary** – Increase our **word database size**, improving sentence fluency and adding more complex phrases.
2. **Personalized Signing Styles** – Enable users to **customize the signing avatar’s speed, expression, and hand dominance** for a more natural experience.
3. **Improved Fingerspelling Recognition** – Enhance **gesture flexibility and accuracy**, making it easier for beginners to learn and practice ASL.
4. **Real-time ASL-to-Text Translation** – Develop **gesture-to-text capabilities**, allowing users to sign and receive real-time text feedback.
5. **Seamless Meeting Integration** – Improve **virtual camera performance** for smoother integration into platforms like Zoom, Teams, and Google Meet.
6. **Community Engagement** – Allow **ASL experts and Deaf users** to contribute feedback and help refine gesture accuracy.

We’re committed to making **SignFlow smarter, more inclusive, and the go-to tool for ASL communication.**

### **Reference**

https://arxiv.org/abs/2408.09311
