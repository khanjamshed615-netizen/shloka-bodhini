# श्लोकबोधिनी · Shloka Bodhini

आयुर्वेदीय संस्कृत श्लोकों के लिए एक मुफ़्त app/website।

* **श्लोक व्याख्या**: पदच्छेद, अन्वय, हर शब्द का अर्थ, भावार्थ, विस्तृत व्याख्या और आयुर्वेदीय सन्दर्भ, हिन्दी और English दोनों में। यह व्याख्या Google Gemini (मुफ़्त key) बनाता है।
* **कोश-पाठ**: हर शब्द के नीचे शब्दकल्पद्रुम, वाचस्पत्यम्, अमरकोश, Monier-Williams और Apte का मूल पाठ दिखता है। ये पाठ app के अन्दर रखे डिजिटल कोशों से आते हैं, AI से नहीं।
* **कोश खोज**: किसी भी शब्द को सीधे पाँचों कोशों में खोजें। इसके लिए key नहीं चाहिए।
* फ़ोन या laptop पर **Install** करके app की तरह चलाएँ। एक बार खोले गए कोश-पृष्ठ बिना इंटरनेट भी खुलते हैं।

---

## तरीका 1: GitHub Pages पर मुफ़्त website (सबसे आसान, सलाह इसी की है)

इस तरीके में हर उपयोगकर्ता "सेटिंग" में अपनी मुफ़्त Gemini key एक बार डालता है। कोश खोज बिना key के चलती है।

1. **GitHub खाता बनाएँ**: [github.com/signup](https://github.com/signup) (मुफ़्त)।
2. **GitHub Desktop install करें**: [desktop.github.com](https://desktop.github.com) और उसी खाते से साइन-इन करें। Folder में हज़ारों फ़ाइलें हैं, और GitHub की website से एक बार में केवल 100 फ़ाइलें upload होती हैं, इसलिए Desktop app ज़रूरी है।
3. GitHub Desktop में **File → New repository** चुनें:
   * Name: `shloka-bodhini`
   * Local path: कोई भी folder, जैसे Documents
   * **Create repository** दबाएँ।
4. Zip खोलें और `shloka-bodhini` folder के **अन्दर की सारी फ़ाइलें** (index.html, app.js, data, fonts, icons…) नए बने repository folder में copy करें। छिपी हुई `.nojekyll` फ़ाइल भी copy होनी चाहिए।
5. GitHub Desktop में नीचे Summary में "website" लिखें, फिर **Commit to main** दबाएँ। उसके बाद ऊपर **Publish repository** दबाएँ, और **"Keep this code private" का निशान हटा दें**, क्योंकि मुफ़्त Pages के लिए repository public होनी चाहिए। Upload में कुछ मिनट लगेंगे।
6. github.com पर अपनी repository खोलें, फिर **Settings → Pages** में जाएँ। "Build and deployment" में Source: **Deploy from a branch** चुनें, Branch: **main** और **/(root)** रखें, फिर **Save** दबाएँ।
7. 2 से 5 मिनट बाद आपकी website इस पते पर खुलेगी:
   `https://आपका-username.github.io/shloka-bodhini/`

### Gemini की मुफ़्त key

1. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) खोलें और Google खाते से साइन-इन करें।
2. **Create API key** दबाएँ। इसमें कार्ड या भुगतान नहीं लगता।
3. Website में **सेटिंग** tab खोलें, key paste करें, फिर **key जाँचें** और **सहेजें** दबाएँ।

Key केवल उसी ब्राउज़र में रहती है। हर व्यक्ति अपनी key डालेगा, इसलिए किसी की सीमा दूसरे पर असर नहीं डालती।

---

## तरीका 2: Vercel पर, ताकि पढ़ने वालों को key न डालनी पड़े

इसमें आपकी एक key सबके लिए काम करती है। ध्यान रखें कि मुफ़्त सीमा सभी उपयोगकर्ताओं में बँट जाएगी, और ज़्यादा लोग होने पर सीमा जल्दी भर सकती है।

1. पहले तरीका 1 के step 1 से 5 तक करें, यानी कोड GitHub पर पहुँचा दें।
2. [vercel.com](https://vercel.com) पर **Continue with GitHub** से मुफ़्त खाता बनाएँ।
3. **Add New → Project** चुनें, `shloka-bodhini` repository के आगे **Import** दबाएँ।
4. **Environment Variables** में Name `GEMINI_API_KEY` और Value में अपनी key डालें, फिर **Deploy** दबाएँ।
5. आपकी website `https://shloka-bodhini.vercel.app` (या मिलते-जुलते पते) पर खुलेगी। अब visitors को key नहीं डालनी पड़ेगी।

---

## App की तरह install करना

* **Laptop (Chrome/Edge)**: website खोलें, address bar में दाईं ओर **Install** का निशान दबाएँ।
* **Android (Chrome)**: ⋮ menu खोलें, फिर **Add to Home screen / Install app** चुनें।
* **iPhone (Safari)**: Share बटन दबाएँ, फिर **Add to Home Screen** चुनें।

## स्रोत और लाइसेंस

* शब्दकल्पद्रुम, वाचस्पत्यम्, Monier-Williams (1899), Apte (1890): [Cologne Digital Sanskrit Dictionaries](https://www.sanskrit-lexicon.uni-koeln.de/), `sanskrit-lexicon/csl-orig`।
* अमरकोश: University of Hyderabad (Amba Kulkarni) का अमरकोश ontology डेटा, [indic-dict/stardict-sanskrit](https://github.com/indic-dict/stardict-sanskrit) के माध्यम से।
* Fonts: Tiro Devanagari Sanskrit और Mukta (SIL Open Font License, `fonts/` में)।
* व्याख्या AI द्वारा बनाई जाती है। शोध में उद्धृत करने से पहले मूल ग्रन्थ और टीका से मिलान करें।

`tools/` folder में कोश-डेटा फिर से बनाने की Python scripts हैं। सामान्य उपयोग में इनकी ज़रूरत नहीं पड़ती।
