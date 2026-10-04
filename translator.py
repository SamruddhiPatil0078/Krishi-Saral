"""
translator.py
--------------
Handles the English | Marathi language option.

This app works fully offline (no external translation API), so
Marathi support is done with:
  1. Fixed, accurate translations for all UI labels and section
     headings (these are always correct, since they're pre-written).
  2. A word/phrase substitution dictionary that swaps common
     policy-related English words for their Marathi equivalents in
     the already-simplified sentences.

This is a best-effort word-level translation, good enough for a
college demo. It is clearly separated here so a real translation
API/model could be swapped in later without touching the rest of the
app.
"""

import re

UI_LABELS = {
    "English": {
        "app_name": "Krishi Saral",
        "tagline": "Government schemes in simple language",
        "simple_explanation": "Simple Explanation",
        "who_can_apply": "Who Can Apply?",
        "benefits": "Benefits",
        "documents": "Documents Required",
        "how_to_apply": "How to Apply?",
        "dates": "Important Dates",
        "conditions": "Important Conditions",
        "exclusions": "Who Cannot Apply?",
        "verification": "Verification Process",
        "payment_method": "How is the money paid?",
        "grievance": "Help & Grievances",
        "eligibility_title": "Quick Eligibility Check",
        "farmer_cat": "Farmer Category",
        "cat_marginal": "Marginal (Up to 1 Hectare)",
        "cat_small": "Small (1 to 2 Hectares)",
        "cat_large": "Large (More than 2 Hectares)",
        "land_records": "Valid Land Records?",
        "bank_acc": "Aadhaar-linked Bank Account?",
        "yes": "Yes",
        "no": "No",
        "check_btn": "Check My Status",
    },
    "Marathi": {
        "app_name": "कृषी सरळ",
        "tagline": "सरकारी योजना सोप्या भाषेत समजून घ्या",
        "simple_explanation": "सोपे स्पष्टीकरण",
        "who_can_apply": "कोण अर्ज करू शकतो?",
        "benefits": "फायदे",
        "documents": "आवश्यक कागदपत्रे",
        "how_to_apply": "अर्ज कसा करावा?",
        "dates": "महत्त्वाच्या तारखा",
        "conditions": "महत्त्वाच्या अटी",
        "exclusions": "कोण अर्ज करू शकत नाही?",
        "verification": "पडताळणी प्रक्रिया",
        "payment_method": "पैसे कसे दिले जातात",
        "grievance": "तक्रार प्रक्रिया",
        "eligibility_title": "त्वरित पात्रता तपासा",
        "farmer_cat": "शेतकरी वर्ग",
        "cat_marginal": "अत्यल्प भूधारक (१ हेक्टरपर्यंत)",
        "cat_small": "अल्प भूधारक (१ ते २ हेक्टर)",
        "cat_large": "मोठे शेतकरी (२ हेक्टरपेक्षा जास्त)",
        "land_records": "वैध जमिनीचा दाखला आहे का?",
        "bank_acc": "आधार-संलग्न बँक खाते आहे का?",
        "yes": "होय",
        "no": "नाही",
        "check_btn": "माझी पात्रता तपासा",
    },
}

WORD_TRANSLATIONS = [
    # Full phrases and clauses (translated first)
    (r"\bThe Small and Marginal Farmer Support Scheme \(SMFSS\) is a sample agricultural support programme designed to demonstrate how a government policy can be converted into simple language\b", "SMFSS ही एक नमुना सरकारी मदत योजना आहे जी पात्र शेतकऱ्यांना शेती साहित्य, पाणी वाचवणारी उपकरणे, साठवणूक आणि काढणीपश्चात कामांसाठी मदत करते"),
    (r"\bThe scheme aims to provide\b", "योजनेचे उद्दिष्ट आहे की"),
    (r"\bfarm inputs, water-saving equipment, and selected post-harvest activities\b", "शेती साहित्य, पाणी वाचवणारी उपकरणे आणि निवडक काढणीपश्चात कामे"),
    (r"\bReduce the financial burden of essential agricultural inputs\b", "अत्यावश्यक कृषी साहित्याचा आर्थिक भार कमी करणे"),
    (r"\bSupport small and marginal\b", "अल्प आणि अत्यल्प शेतकऱ्यांना"),
    (r"\bin improving farm productivity\b", "शेतीची उत्पादकता वाढवण्यासाठी मदत करणे"),
    (r"\bEligibility a farmer may be eligible if the\b", "पात्रता: शेतकरी पात्र असू शकतो जर तो"),
    (r"\bis an Indian\b", "एक भारतीय"),
    (r"\bcultivating agricultural land in the participating state\b", "सहभागी राज्यात कृषी जमिनीवर शेती करणारा असेल"),
    (r"\bPriority may be given to small and marginal\b", "अल्प आणि अत्यल्प शेतकऱ्यांना प्राधान्य दिले जाऊ शकते"),
    (r"\bMicro-irrigation equipment\b", "सूक्ष्म-सिंचन उपकरणे"),
    (r"\bUp to 50% of eligible cost\b", "पात्र खर्चाच्या ५०% पर्यंत"),
    (r"\bMinimum 50%\b", "किमान ५०%"),
    (r"\bshould have valid land or cultivation records\b", "कडे वैध जमिनीचा किंवा लागवडीचा दाखला असावा"),
    (r"\band a bank account capable of receiving direct benefit transfers\b", "आणि थेट लाभ हस्तांतरण (DBT) मिळवण्यास सक्षम असलेले बँक खाते असावे"),
    (r"\bIdentity proof such as Aadhaar or another accepted government identity\b", "आधार किंवा इतर स्वीकार्य सरकारी ओळखपत्रासारखा ओळखीचा पुरावा"),
    (r"\bProof of land ownership, tenancy, or cultivation as applicable\b", "लागू असल्याप्रमाणे जमिनीची मालकी, कुळवाट किंवा लागवडीचा पुरावा"),
    (r"\bBank account details and IFSC code\b", "बँक खात्याचा तपशील आणि IFSC कोड"),
    (r"\bRecent photograph of the\b", "चा अलीकडील फोटो"),
    (r"\bUpload or submit the required\b", "आवश्यक कागदपत्रे अपलोड करा किंवा सबमिट करा"),
    (r"\bMobile number registered for application-related communication\b", "अर्जाशी संबंधित संवादासाठी नोंदणीकृत मोबाईल क्रमांक"),
    (r"\bVisit the designated agriculture department portal or authorized service centre\b", "निर्धारित कृषी विभाग पोर्टल किंवा अधिकृत सेवा केंद्राला भेट द्या"),
    (r"\bComplete the farmer registration form with personal and agricultural details\b", "वैयक्तिक आणि कृषी तपशीलांसह शेतकरी नोंदणी फॉर्म पूर्ण करा"),
    (r"\bSubmit the application and save the acknowledgement number\b", "अर्ज सबमिट करा आणि पोचपावती क्रमांक जतन करा"),
    (r"\bneed to register, submit the required\b", "नोंदणी करणे, आवश्यक कागदपत्रे सादर करणे आवश्यक आहे"),
    (r"\bchoose an eligible benefit, and wait for verification\b", "पात्र लाभ निवडा आणि पडताळणीची प्रतीक्षा करा"),
    (r"\bFor this sample policy, applications are accepted from\b", "या नमुना धोरणासाठी, अर्ज स्वीकारले जातील"),
    (r"\bApplications submitted after the closing date may be considered only if the implementing authority extends the application period\b", "अंतिम तारखेनंतर सबमिट केलेले अर्ज फक्त अंमलबजावणी अधिकाऱ्याने अर्जाचा कालावधी वाढवल्यासच विचारात घेतले जाऊ शकतात"),
    (r"\bAssistance is based on availability of funds and verification of eligibility\b", "मदत निधीच्या उपलब्धतेवर आणि पात्रतेच्या पडताळणीवर आधारित आहे"),
    (r"\bmust provide correct information\b", "योग्य माहिती देणे आवश्यक आहे"),
    (r"\bApplications containing false or misleading information may be rejected\b", "चुकीची किंवा दिशाभूल करणारी माहिती असलेले अर्ज नाकारले जाऊ शकतात"),
    (r"\bThe same expense should not be claimed under multiple components of this scheme unless specifically permitted by the implementing authority\b", "अंमलबजावणी अधिकाऱ्याने विशेष परवानगी दिल्याशिवाय या योजनेच्या अनेक घटकाअंतर्गत एकाच खर्चाचा दावा करू नये"),
    (r"\bThe application is verified by the concerned authority before approval\b", "मंजुरीपूर्वी संबंधित अधिकाऱ्याद्वारे अर्जाची पडताळणी केली जाते"),
    (r"\bApplications are checked and approved after eligibility and documents are verified\b", "पात्रता आणि कागदपत्रे तपासल्यानंतर अर्ज तपासले जातात आणि मंजूर केले जातात"),
    (r"\bApproved assistance is transferred to the eligible beneficiary\b", "मंजूर केलेली मदत पात्र लाभार्थ्याकडे हस्तांतरित केली जाते"),
    (r"\bwhose eligibility has been verified and whose assistance has been sanctioned\b", "ज्यांची पात्रता तपासली गेली आहे आणि ज्यांची मदत मंजूर केली गेली आहे"),
    (r"\bIf approved, the financial help is transferred to the registered\b", "मंजूर झाल्यास, आर्थिक मदत नोंदणीकृत बँक खात्यात हस्तांतरित केली जाते"),
    (r"\bmay contact the local agriculture office or the designated service centre for assistance\b", "मदतीसाठी स्थानिक कृषी कार्यालय किंवा निर्धारित सेवा केंद्राशी संपर्क साधू शकतात"),
    (r"\bA grievance should include the application acknowledgement number\b", "तक्रारीमध्ये अर्जाचा पोचपावती क्रमांक असावा"),
    (r"\bname, registered mobile number, and a clear description of the issue\b", "नाव, नोंदणीकृत मोबाईल क्रमांक आणि समस्येचे स्पष्ट वर्णन"),

    # Mid-size phrases and keywords
    (r"\bfarmers who qualify\b", "पात्र शेतकरी"),
    (r"\bfinancial help\b", "आर्थिक मदत"),
    (r"\bsubsidy\b", "अनुदान"),
    (r"\bdocuments Required\b", "आवश्यक कागदपत्रे"),
    (r"\bdocuments\b", "कागदपत्रे"),
    (r"\bdocument\b", "कागदपत्र"),
    (r"\bbank account\b", "बँक खाते"),
    (r"\baadhaar card\b", "आधार कार्ड"),
    (r"\bland record\b", "जमिनीचा दाखला"),
    (r"\bapply\b", "अर्ज करा"),
    (r"\bapplication\b", "अर्ज"),
    (r"\bregister\b", "नोंदणी करा"),
    (r"\bonline\b", "ऑनलाईन"),
    (r"\boffline\b", "ऑफलाईन"),
    (r"\bdeadline\b", "अंतिम मुदत"),
    (r"\blast date\b", "शेवटची तारीख"),
    (r"\bbefore\b", "आधी"),
    (r"\bmust\b", "आवश्यक आहे"),
    (r"\brequired\b", "आवश्यक"),
    (r"\bcan get\b", "मिळू शकते"),
    (r"\bcan apply\b", "अर्ज करू शकतो"),
    (r"\bmeet the required conditions\b", "आवश्यक अटी पूर्ण करतात"),
    (r"\byear\b", "वर्ष"),
    (r"\bmonth\b", "महिना"),
    (r"\bamount\b", "रक्कम"),
    (r"\bper acre\b", "प्रति एकर"),
    (r"\bper hectare\b", "प्रति हेक्टर"),
    (r"\bfarmers\b", "शेतकरी"),
    (r"\bfarmer\b", "शेतकरी"),
    (r"\bthe\b", ""),
    (r"\bis\b", "आहे"),
    (r"\band\b", "आणि"),
    (r"\bor\b", "किंवा"),
    (r"\bfor\b", "साठी"),
    (r"\bin\b", "मध्ये"),
    (r"\bof\b", "चे"),
    (r"\bto\b", "ला"),
    (r"\bwith\b", "सह"),
    (r"\bgovernment\b", "सरकारी"),
    (r"\bscheme\b", "योजना"),
    (r"\bpolicy\b", "धोरण"),
    (r"\beligible\b", "पात्र"),
    (r"\bsmall\b", "लहान"),
    (r"\bmarginal\b", "अत्यल्प"),
    (r"\bequipment\b", "उपकरणे"),
    (r"\bapproved\b", "मंजूर"),
    (r"\bassistance\b", "सहाय्य"),
    (r"\bdetails\b", "तपशील"),
    (r"\bvalid\b", "वैध"),
    (r"\bagricultural\b", "कृषी"),
    (r"\bland\b", "जमीन"),
    (r"\brejected\b", "नाकारले"),
    (r"\bprocess\b", "प्रक्रिया"),
    (r"\bbenefit\b", "लाभ"),
]

_COMPILED_WORDS = [(re.compile(p, re.IGNORECASE), r) for p, r in WORD_TRANSLATIONS]


def get_labels(language):
    """Return the dictionary of UI label strings for the chosen language."""
    return UI_LABELS.get(language, UI_LABELS["English"])


def translate_sentence_to_marathi(sentence):
    translated = sentence
    for pattern, replacement in _COMPILED_WORDS:
        translated = pattern.sub(replacement, translated)
    return translated


def translate_text(sentences, language):
    """
    Apply the language option to a list of already-simplified
    sentences.
    """
    if language == "Marathi":
        return [translate_sentence_to_marathi(s) for s in sentences]
    return sentences
