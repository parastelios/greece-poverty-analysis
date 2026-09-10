"""Greek strings for the figures in the Greek narrative edition.

Every reader-facing string inside a figure is translated here and nowhere
else. 92_build_narrative_el.py looks each one up and FAILS THE BUILD on a
miss, so a new or renamed label in the English figures cannot reach a Greek
reader untranslated: the build stops and names the string.

What is deliberately NOT here: the data values, the series order, the figure
ids, the claim anchors and the chart tone names (chart-gr, chart-neutral and
friends, which are CSS class fragments the JS reads, not text). Translating
any of those would change what the chart says or stop it rendering.
"""

# ---------------------------------------------------------------------------
# Country names. The chart draws all 27 member states, so these appear as
# series labels, scatter point labels and table row labels alike.
# ---------------------------------------------------------------------------
COUNTRIES = {
    "Austria": "Αυστρία", "Belgium": "Βέλγιο", "Bulgaria": "Βουλγαρία",
    "Croatia": "Κροατία", "Cyprus": "Κύπρος", "Czechia": "Τσεχία",
    "Denmark": "Δανία", "Estonia": "Εσθονία", "Finland": "Φινλανδία",
    "France": "Γαλλία", "Germany": "Γερμανία", "Greece": "Ελλάδα",
    "Hungary": "Ουγγαρία", "Ireland": "Ιρλανδία", "Italy": "Ιταλία",
    "Latvia": "Λετονία", "Lithuania": "Λιθουανία",
    "Luxembourg": "Λουξεμβούργο", "Malta": "Μάλτα",
    "Netherlands": "Κάτω Χώρες", "Poland": "Πολωνία",
    "Portugal": "Πορτογαλία", "Romania": "Ρουμανία",
    "Slovakia": "Σλοβακία", "Slovenia": "Σλοβενία", "Spain": "Ισπανία",
    "Sweden": "Σουηδία",
}

# ---------------------------------------------------------------------------
# Tab names. These are quoted verbatim in the article's own prose, so the two
# have to agree: a reader told to open «Πόσοι δείκτες» must find that tab.
# ---------------------------------------------------------------------------
TABS = {
    "How Greece's hardship gap developed": "Πώς εξελίχθηκε το χάσμα",
    "Where countries stood in 2024": "Πού βρίσκονταν οι χώρες το 2024",
    "Unexpected expenses": "Απρόοπτα έξοδα",
    "Material deprivation": "Υλική στέρηση",
    "Keeping the home warm": "Θέρμανση του σπιτιού",
    "Falling behind on bills": "Καθυστερήσεις σε λογαριασμούς",
    "Which measures": "Ποιοι δείκτες",
    "How many measures": "Πόσοι δείκτες",
    "Who falls below a fixed line": "Ποιοι είναι κάτω από σταθερό όριο",
    "What the line itself is worth": "Πόσο αξίζει το ίδιο το όριο",
    "Headline measures": "Βασικοί δείκτες",
    "Components": "Συστατικά",
    "By age": "Κατά ηλικία",
    "By sex": "Κατά φύλο",
    "Long-term unemployment": "Μακροχρόνια ανεργία",
    "Material resources": "Πραγματική κατανάλωση",
    "Wage-adjusted affordability": "Αγοραστική πίεση",
    "Accumulated unemployment": "Συσσωρευμένη ανεργία",
    "Years wages below 2008": "Χρόνια μισθών κάτω από το 2008",
    "Housing deterioration since 2010": "Επιδείνωση κόστους στέγασης",
    "Between vs within": "Μεταξύ ή εντός χωρών",
}

# ---------------------------------------------------------------------------
# Series, scatter-point and table-row labels.
# ---------------------------------------------------------------------------
LABELS = {
    # age and sex groups
    "65 and over": "65 και άνω", "Under 18": "Κάτω των 18",
    "All": "Σύνολο", "All ages": "Όλες οι ηλικίες",
    "Men": "Άνδρες", "Women": "Γυναίκες",
    "EU: 18-24": "ΕΕ: 18-24", "EU: 25-49": "ΕΕ: 25-49",
    "EU: 50-64": "ΕΕ: 50-64", "EU: 65 and over": "ΕΕ: 65 και άνω",
    "EU: all": "ΕΕ: σύνολο", "EU: all ages": "ΕΕ: όλες οι ηλικίες",
    "EU: men": "ΕΕ: άνδρες", "EU: women": "ΕΕ: γυναίκες",
    "EU: under 18": "ΕΕ: κάτω των 18",
    # medians
    "EU median": "Διάμεση τιμή ΕΕ",
    "EU-country median": "Διάμεσος των χωρών της ΕΕ",
    # paired measure/country series
    "AROPE: EU median": "AROPE: διάμεσος ΕΕ",
    "AROPE: Greece": "AROPE: Ελλάδα",
    "Income poverty: EU median": "Εισοδηματική φτώχεια: διάμεσος ΕΕ",
    "Income poverty: Greece": "Εισοδηματική φτώχεια: Ελλάδα",
    "Material deprivation: EU median": "Υλική στέρηση: διάμεσος ΕΕ",
    "Material deprivation: Greece": "Υλική στέρηση: Ελλάδα",
    "Reported hardship: EU median": "Οικονομική δυσκολία: διάμεσος ΕΕ",
    "Reported hardship: Greece": "Οικονομική δυσκολία: Ελλάδα",
    "EU median: falling behind on bills":
        "Διάμεσος ΕΕ: καθυστερήσεις σε λογαριασμούς",
    "EU median: income poverty": "Διάμεσος ΕΕ: εισοδηματική φτώχεια",
    "EU median: keeping the home warm": "Διάμεσος ΕΕ: θέρμανση του σπιτιού",
    "EU median: material deprivation": "Διάμεσος ΕΕ: υλική στέρηση",
    "EU median: reported hardship": "Διάμεσος ΕΕ: οικονομική δυσκολία",
    "EU median: unexpected expenses": "Διάμεσος ΕΕ: απρόοπτα έξοδα",
    "Greece: current-year threshold": "Ελλάδα: όριο της χρονιάς",
    "Greece: falling behind on bills": "Ελλάδα: καθυστερήσεις σε λογαριασμούς",
    "Greece: fixed 2008 threshold": "Ελλάδα: σταθερό όριο του 2008",
    "Greece: income poverty": "Ελλάδα: εισοδηματική φτώχεια",
    "Greece: keeping the home warm": "Ελλάδα: θέρμανση του σπιτιού",
    "Greece: material deprivation": "Ελλάδα: υλική στέρηση",
    "Greece: reported hardship": "Ελλάδα: οικονομική δυσκολία",
    "Greece: unexpected expenses": "Ελλάδα: απρόοπτα έξοδα",
    "Same threshold in 2008 purchasing power":
        "Το ίδιο όριο σε αγοραστική δύναμη 2008",
    "Threshold in cash terms": "Το όριο σε τρέχουσες τιμές",
    "Median EU country: poverty 15.5%, hardship 17.1%":
        "Μεσαία χώρα ΕΕ: φτώχεια 15,5%, δυσκολία 17,1%",
    "Median EU: 15.5%, 17.1%": "Μεσαία ΕΕ: 15,5%, 17,1%",
    "Greece: income poverty 19.6%, hardship 66.7%":
        "Ελλάδα: εισοδηματική φτώχεια 19,6%, δυσκολία 66,7%",
    # indicators
    "AROPE": "AROPE",
    "Accumulated affordability pressure": "Συσσωρευμένη αγοραστική πίεση",
    "Accumulated unemployment": "Συσσωρευμένη ανεργία",
    "Citizens leaving the country": "Πολίτες που φεύγουν από τη χώρα",
    "Compounded inflation since 2008": "Σύνθετος πληθωρισμός από το 2008",
    "Cumulative GDP shortfall": "Σωρευτικό έλλειμμα ΑΕΠ",
    "Cumulative threshold shortfall": "Σωρευτικό έλλειμμα ορίου",
    "Cumulative wage shortfall": "Σωρευτικό μισθολογικό έλλειμμα",
    "Economic output per person": "Οικονομικό προϊόν ανά άτομο",
    "Food prices": "Τιμές τροφίμων",
    "Hardship gap against AROPE": "Χάσμα δυσκολίας έναντι AROPE",
    "Hardship gap against income poverty":
        "Χάσμα έναντι εισοδηματικής φτώχειας",
    "Hours worked against hourly pay": "Ώρες έναντι ωριαίας αμοιβής",
    "Hours worked each week": "Ώρες εργασίας την εβδομάδα",
    "Household income after inflation": "Εισόδημα μετά τον πληθωρισμό",
    "Housing and energy prices": "Τιμές στέγασης και ενέργειας",
    "Housing deterioration since 2010": "Επιδείνωση κόστους στέγασης",
    "Housing-cost overburden": "Επιβάρυνση κόστους στέγασης",
    "Income inequality": "Εισοδηματική ανισότητα",
    "Income poverty (AROP)": "Εισοδηματική φτώχεια (AROP)",
    "Keeping the home warm": "Θέρμανση του σπιτιού",
    "Long-term unemployment": "Μακροχρόνια ανεργία",
    "Material deprivation": "Υλική στέρηση",
    "Material resources": "Πραγματική κατανάλωση",
    "Pay per hour worked": "Αμοιβή ανά ώρα εργασίας",
    "Prices measured against wages": "Τιμές σε σχέση με τους μισθούς",
    "Prices overall": "Γενικό επίπεδο τιμών",
    "Real household income": "Πραγματικό εισόδημα",
    "Real poverty threshold": "Πραγματικό όριο φτώχειας",
    "Real wages": "Πραγματικοί μισθοί",
    "Reported hardship": "Οικονομική δυσκολία",
    "Share below own GDP peak": "Απόσταση από την κορύφωση ΑΕΠ",
    "The poverty line after inflation": "Το όριο φτώχειας μετά τον πληθωρισμό",
    "Wage-adjusted affordability": "Αγοραστική πίεση",
    "Wages after inflation": "Μισθοί μετά τον πληθωρισμό",
    "What households actually spend": "Τι ξοδεύουν τα νοικοκυριά",
    "What households expect of the year ahead":
        "Προσδοκίες νοικοκυριών για τον χρόνο",
    "Years wages below 2008": "Χρόνια μισθών κάτω από το 2008",
    # categorical cell values in the breadth table
    "entered worst fifth": "μπήκε στο χειρότερο πέμπτο",
    "already worst fifth": "ήδη στο χειρότερο πέμπτο",
    "outside both years": "εκτός και τις δύο χρονιές",
}

# ---------------------------------------------------------------------------
# Axes, legends and the small print drawn onto the chart itself.
# ---------------------------------------------------------------------------
CHROME = {
    # y axes
    "% of age group": "% της ηλικιακής ομάδας",
    "% of labour force": "% του εργατικού δυναμικού",
    "% of labour force, higher = worse":
        "% του εργατικού δυναμικού, όσο πιο ψηλά τόσο χειρότερα",
    "% of people": "% του πληθυσμού",
    "% of the same 16 indicators, higher = worse":
        "% των ίδιων 16 δεικτών, όσο πιο ψηλά τόσο χειρότερα",
    "Euros per year, single adult": "Ευρώ τον χρόνο, ένας ενήλικας",
    "Index, EU27 = 100": "Δείκτης, ΕΕ27 = 100",
    "Index, EU27 = 100, higher = worse":
        "Δείκτης, ΕΕ27 = 100, όσο πιο ψηλά τόσο χειρότερα",
    "PPS per head": "ΜΑΔ ανά άτομο",
    "PPS per head, lower = worse": "ΜΑΔ ανά άτομο, όσο πιο χαμηλά τόσο χειρότερα",
    "Percent": "Ποσοστό",
    "Points from own 2015-2024 average":
        "Μονάδες από τον δικό του μέσο όρο 2015-2024",
    "Reported hardship, percent of households":
        "Οικονομική δυσκολία, % των νοικοκυριών",
    # x axes
    "Income poverty, percent of people": "Εισοδηματική φτώχεια, % του πληθυσμού",
    "Residual, pp: positive = MORE hardship than predicted, negative = less":
        "Ανεξήγητο υπόλοιπο, σε ποσοστιαίες μονάδες: θετικό = ΜΕΓΑΛΥΤΕΡΗ "
        "δυσκολία από την προβλεπόμενη, αρνητικό = μικρότερη",
    "Share of the 2015 Greece-EU gap closed by 2024 (1.0 = fully closed; "
    "above 1.0 = overshot and reversed)":
        "Πόσο από το χάσμα Ελλάδας-ΕΕ του 2015 έκλεισε ως το 2024 (1,0 = "
        "έκλεισε πλήρως· πάνω από 1,0 = αντιστράφηκε)",
    "Standardised effect (SD of hardship)":
        "Τυποποιημένη επίδραση (τυπικές αποκλίσεις δυσκολίας)",
    "position in the EU distribution, 0 = best, 100 = worst":
        "θέση στην κατανομή της ΕΕ, 0 = καλύτερη, 100 = χειρότερη",
    # context-line legends
    "Each other EU country": "Κάθε άλλη χώρα της ΕΕ",
    "Each other EU country: long-term unemployment":
        "Κάθε άλλη χώρα της ΕΕ: μακροχρόνια ανεργία",
    "Each other EU country: material resources":
        "Κάθε άλλη χώρα της ΕΕ: πραγματική κατανάλωση",
    "Each other EU country: reported hardship":
        "Κάθε άλλη χώρα της ΕΕ: οικονομική δυσκολία",
    "Each other EU country: wage-adjusted affordability":
        "Κάθε άλλη χώρα της ΕΕ: αγοραστική πίεση",
    # reference lines, legends, zero labels
    "no change": "καμία μεταβολή",
    "no effect": "καμία επίδραση",
    "predicted exactly": "ακριβώς όπως προβλέφθηκε",
    "within countries": "εντός χωρών",
    "between countries": "μεταξύ χωρών",
    "frozen specification": "βασικό μοντέλο",
    "deprivation-free companion": "εκδοχή χωρίς τη στέρηση",
    "Peer relationship, Greece excluded":
        "Σχέση των υπόλοιπων χωρών, χωρίς την Ελλάδα",
    "Peer relationship": "Σχέση των υπόλοιπων χωρών",
    "{gap} points above the peer prediction":
        "{gap} μονάδες πάνω από την πρόβλεψη",
    "+{gap} vs peers": "+{gap} έναντι πρόβλεψης",
    # units shown in tooltips
    "consecutive years below the 2008 level":
        "συνεχόμενα χρόνια κάτω από το επίπεδο του 2008",
    "of the 2015 gap": "του χάσματος του 2015",
    "percentage-point-years above 2009": "μονάδες-έτη πάνω από το 2009",
    "percentage-point-years above 2010": "μονάδες-έτη πάνω από το 2010",
    # the breadth chart's own inline legend, drawn as HTML
    "entered the worst fifth (7)": "μπήκαν στο χειρότερο πέμπτο (7)",
    "already in it in 2008 (4)": "ήταν ήδη εκεί το 2008 (4)",
    "outside in both years (5)": "εκτός και τις δύο χρονιές (5)",
    # evidence-tier badges (hidden by CSS in this edition, present in the DOM)
    "descriptive": "περιγραφικό",
    "descriptive corroboration": "περιγραφική επιβεβαίωση",
    "post-selection robustness": "έλεγχος ευρωστίας μετά την επιλογή",
    "pre-planned confirmatory": "προσχεδιασμένη επιβεβαιωτική ανάλυση",
}

# ---------------------------------------------------------------------------
# Fallback-table headers.
# ---------------------------------------------------------------------------
HEADERS = {
    "Series": "Σειρά",
    "Year": "Έτος",
    "Country": "Χώρα",
    "Measure": "Δείκτης",
    "Change": "Μεταβολή",
    "Transition": "Μετάβαση",
    "Income poverty (%)": "Εισοδηματική φτώχεια (%)",
    "Reported hardship (%)": "Οικονομική δυσκολία (%)",
    "2008 position": "Θέση 2008",
    "2024 position": "Θέση 2024",
    "Share of 2015 gap closed": "Πόσο έκλεισε από το χάσμα του 2015",
    "Greece 2015": "Ελλάδα 2015",
    "Greece 2024": "Ελλάδα 2024",
    "EU median 2015": "Διάμεση τιμή ΕΕ 2015",
    "EU median 2024": "Διάμεση τιμή ΕΕ 2024",
    "Gap 2015": "Χάσμα 2015",
    "Gap 2024": "Χάσμα 2024",
    "Accumulated measure": "Συσσωρευμένος δείκτης",
    "Between (SD)": "Μεταξύ χωρών (τ.α.)",
    "Within (SD)": "Εντός χωρών (τ.α.)",
    "Between p": "p μεταξύ χωρών",
    "Within p": "p εντός χωρών",
    "First difference (raw)": "Πρώτη διαφορά",
    "First difference p": "p πρώτης διαφοράς",
    "Reference specification": "Βασικό μοντέλο",
    "Deprivation-free companion": "Εκδοχή χωρίς τη στέρηση",
    "Accumulated unemployment (percentage-point-years above 2009)":
        "Συσσωρευμένη ανεργία (μονάδες-έτη πάνω από το 2009)",
    "Years wages below 2008 (consecutive years below the 2008 level)":
        "Χρόνια με μισθούς κάτω από το 2008 (συνεχόμενα χρόνια κάτω από το "
        "επίπεδο του 2008)",
    "Housing deterioration since 2010 (percentage-point-years above 2010)":
        "Επιδείνωση κόστους στέγασης (μονάδες-έτη πάνω από το 2010)",
}

# ---------------------------------------------------------------------------
# The question under each figure.
# ---------------------------------------------------------------------------
QUESTIONS = {
    "Does official income poverty account for the hardship Greek households "
    "report?":
        "Εξηγεί η επίσημη εισοδηματική φτώχεια τη δυσκολία που δηλώνουν τα "
        "ελληνικά νοικοκυριά;",
    "Did concrete affordability difficulties rise and fall with what Greek "
    "households reported?":
        "Ανέβαιναν και κατέβαιναν οι συγκεκριμένες οικονομικές δυσκολίες μαζί "
        "με όσα δήλωναν τα ελληνικά νοικοκυριά;",
    "Did Greek disadvantage deepen on a few measures, or spread across many?":
        "Βάθυνε το ελληνικό μειονέκτημα σε λίγους δείκτες, ή απλώθηκε σε "
        "πολλούς;",
    "What happened to the line Greek poverty is measured against, and what "
    "does a fixed line show instead?":
        "Τι απέγινε το όριο με το οποίο μετριέται η ελληνική φτώχεια, και τι "
        "δείχνει ένα σταθερό όριο στη θέση του;",
    "What sits behind AROPE, and did every age group move the same way?":
        "Τι κρύβεται πίσω από τον AROPE, και κινήθηκαν το ίδιο όλες οι "
        "ηλικιακές ομάδες;",
    "Which measures converged toward the EU and which diverged?":
        "Ποιοι δείκτες πλησίασαν την ΕΕ και ποιοι απομακρύνθηκαν;",
    "What do the three supported constructs actually look like for Greece "
    "against the EU?":
        "Πώς φαίνονται στην πράξη οι τρεις δείκτες που στηρίχθηκαν, για την "
        "Ελλάδα έναντι της ΕΕ;",
    "How much accumulated unemployment, wage non-recovery and housing-cost "
    "deterioration has each country absorbed, and where does Greece sit?":
        "Πόση συσσωρευμένη ανεργία, καθυστέρηση στην ανάκαμψη των μισθών "
        "και επιδείνωση του κόστους στέγασης έχει απορροφήσει κάθε χώρα, "
        "και πού βρίσκεται η Ελλάδα;",
    "Does the answer depend on which model is chosen?":
        "Εξαρτάται η απάντηση από το ποιο μοντέλο θα διαλέξουμε;",
}

# ---------------------------------------------------------------------------
# The accessibility description of each chart, read aloud by screen readers.
# ---------------------------------------------------------------------------
ALT = {
    "Greek reported hardship and income poverty against the EU median of "
    "each, with every other country's hardship faint behind. The distance "
    "between the blue and green Greek lines never closes":
        "Η ελληνική οικονομική δυσκολία και η εισοδηματική φτώχεια έναντι της "
        "διάμεσης τιμής της ΕΕ για την καθεμία, με τη δυσκολία κάθε άλλης "
        "χώρας αχνά από πίσω. Η απόσταση ανάμεσα στην μπλε και στην πράσινη "
        "ελληνική γραμμή δεν κλείνει ποτέ",
    "Every EU country in 2024 placed by income poverty and reported "
    "hardship. Greece has an ordinary income-poverty rate and an "
    "extraordinary hardship rate, far above the peer line":
        "Κάθε χώρα της ΕΕ το 2024, τοποθετημένη κατά εισοδηματική φτώχεια και "
        "οικονομική δυσκολία. Η Ελλάδα έχει συνηθισμένο ποσοστό εισοδηματικής "
        "φτώχειας και ασυνήθιστο ποσοστό δυσκολίας, πολύ πάνω από τη γραμμή "
        "των υπόλοιπων χωρών",
    "Greek reported hardship, Greek unexpected expenses and the EU median "
    "for unexpected expenses, each as distances from its own average. Greek "
    "correlation 0.92":
        "Η ελληνική οικονομική δυσκολία, τα ελληνικά απρόοπτα έξοδα και η "
        "διάμεση τιμή της ΕΕ για τα απρόοπτα έξοδα, το καθένα ως απόσταση από "
        "τον δικό του μέσο όρο. Ελληνική συσχέτιση 0,92",
    "Greek reported hardship, Greek material deprivation and the EU median "
    "for material deprivation, each as distances from its own average. Greek "
    "correlation 0.94":
        "Η ελληνική οικονομική δυσκολία, η ελληνική υλική στέρηση και η "
        "διάμεση τιμή της ΕΕ για την υλική στέρηση, το καθένα ως απόσταση από "
        "τον δικό του μέσο όρο. Ελληνική συσχέτιση 0,94",
    "Greek reported hardship, Greek keeping the home warm and the EU median "
    "for keeping the home warm, each as distances from its own average. "
    "Greek correlation 0.87":
        "Η ελληνική οικονομική δυσκολία, η ελληνική δυσκολία θέρμανσης του "
        "σπιτιού και η διάμεση τιμή της ΕΕ για τη θέρμανση του σπιτιού, το "
        "καθένα ως απόσταση από τον δικό του μέσο όρο. Ελληνική συσχέτιση 0,87",
    "Greek reported hardship, Greek falling behind on bills and the EU "
    "median for falling behind on bills, each as distances from its own "
    "average. Greek correlation 0.37":
        "Η ελληνική οικονομική δυσκολία, οι ελληνικές καθυστερήσεις σε "
        "λογαριασμούς και η διάμεση τιμή της ΕΕ για τις καθυστερήσεις σε "
        "λογαριασμούς, το καθένα ως απόσταση από τον δικό του μέσο όρο. "
        "Ελληνική συσχέτιση 0,37",
    "The same 16 indicators placed by Greece's position in the EU "
    "distribution in 2008 and again in 2024, with the worst fifth shaded. 7 "
    "entered the band over the period, 4 were already inside it":
        "Οι ίδιοι 16 δείκτες, τοποθετημένοι κατά τη θέση της Ελλάδας στην "
        "κατανομή της ΕΕ το 2008 και ξανά το 2024, με σκιασμένο το χειρότερο "
        "πέμπτο. Επτά μπήκαν στη ζώνη μέσα στην περίοδο, τέσσερις ήταν ήδη "
        "εκεί",
    "The share of the same fixed basket of 16 indicators placing each "
    "country in the EU's worst fifth, every year from 2008 to 2024. Greece "
    "against the EU-country median and every other reporting member state":
        "Το ποσοστό του ίδιου σταθερού καλαθιού 16 δεικτών που τοποθετεί κάθε "
        "χώρα στο χειρότερο πέμπτο της ΕΕ, κάθε χρόνο από το 2008 ως το 2024. "
        "Η Ελλάδα έναντι της διάμεσης τιμής των χωρών της ΕΕ και κάθε άλλου "
        "κράτους-μέλους με στοιχεία",
    "Greek anchored poverty against the floating income-poverty rate":
        "Η ελληνική φτώχεια με αγκυρωμένο όριο έναντι του κινούμενου δείκτη "
        "εισοδηματικής φτώχειας",
    "The Greek poverty threshold in cash terms and in 2008 purchasing power. "
    "The cash line returns close to its peak while the purchasing-power line "
    "stays far below it":
        "Το ελληνικό όριο φτώχειας σε τρέχουσες τιμές και σε αγοραστική δύναμη "
        "του 2008. Η γραμμή σε τρέχουσες τιμές επιστρέφει κοντά στην κορύφωσή "
        "της, ενώ η γραμμή της αγοραστικής δύναμης μένει πολύ πιο κάτω",
    "Income poverty, AROPE and reported hardship for Greece against the EU "
    "median of each, colour marking the measure and dash marking the "
    "country. Reported hardship sits far above the other two, AROPE between "
    "them":
        "Η εισοδηματική φτώχεια, ο AROPE και η οικονομική δυσκολία για την "
        "Ελλάδα έναντι της διάμεσης τιμής της ΕΕ για την καθεμία· το χρώμα "
        "δείχνει τον δείκτη και η διακεκομμένη γραμμή τη χώρα. Η οικονομική "
        "δυσκολία βρίσκεται πολύ πάνω από τις άλλες δύο, ο AROPE ανάμεσά τους",
    "The three AROPE components for Greece against the EU median, colour "
    "marking the measure and dash marking the country. Greece is above the "
    "EU median on all three":
        "Τα τρία συστατικά του AROPE για την Ελλάδα έναντι της διάμεσης τιμής "
        "της ΕΕ· το χρώμα δείχνει τον δείκτη και η διακεκομμένη γραμμή τη "
        "χώρα. Η Ελλάδα είναι πάνω από τη διάμεση τιμή της ΕΕ και στα τρία",
    "Greek AROPE by age group, each paired with the EU median for the same "
    "band in the same colour: Greece solid, Europe dashed":
        "Ο ελληνικός AROPE κατά ηλικιακή ομάδα, κάθε μία μαζί με τη διάμεση "
        "τιμή της ΕΕ για την ίδια ομάδα στο ίδιο χρώμα: η Ελλάδα με συνεχή "
        "γραμμή, η Ευρώπη με διακεκομμένη",
    "Greek AROPE by sex, each paired with the EU median for the same sex in "
    "the same colour: Greece solid, Europe dashed. Greek women sit above "
    "Greek men throughout, and both far above Europe":
        "Ο ελληνικός AROPE κατά φύλο, κάθε ένα μαζί με τη διάμεση τιμή της ΕΕ "
        "για το ίδιο φύλο στο ίδιο χρώμα: η Ελλάδα με συνεχή γραμμή, η Ευρώπη "
        "με διακεκομμένη. Οι Ελληνίδες βρίσκονται πάνω από τους Έλληνες σε "
        "όλη τη διάρκεια, και οι δύο πολύ πάνω από την Ευρώπη",
    "Share of each 2015 Greece-EU gap closed by 2024; positive means "
    "convergence, negative means divergence":
        "Πόσο έκλεισε ως το 2024 από κάθε χάσμα Ελλάδας-ΕΕ του 2015· θετικό "
        "σημαίνει σύγκλιση, αρνητικό απόκλιση",
    "Long-term unemployment for Greece against the EU median and every other "
    "country, in % of labour force":
        "Η μακροχρόνια ανεργία για την Ελλάδα έναντι της διάμεσης τιμής της ΕΕ "
        "και κάθε άλλης χώρας, σε % του εργατικού δυναμικού",
    "Long-term unemployment for Greece against the EU median and every other "
    "country, in % of labour force, higher = worse":
        "Η μακροχρόνια ανεργία για την Ελλάδα έναντι της διάμεσης τιμής της ΕΕ "
        "και κάθε άλλης χώρας, σε % του εργατικού δυναμικού, όσο πιο ψηλά "
        "τόσο χειρότερα",
    "Material resources for Greece against the EU median and every other "
    "country, in PPS per head":
        "Η πραγματική κατανάλωση για την Ελλάδα έναντι της διάμεσης τιμής της ΕΕ και "
        "κάθε άλλης χώρας, σε ΜΑΔ ανά άτομο",
    "Material resources for Greece against the EU median and every other "
    "country, in PPS per head, lower = worse":
        "Η πραγματική κατανάλωση για την Ελλάδα έναντι της διάμεσης τιμής της ΕΕ και "
        "κάθε άλλης χώρας, σε ΜΑΔ ανά άτομο, όσο πιο χαμηλά τόσο χειρότερα",
    "Wage-adjusted affordability for Greece against the EU median and every "
    "other country, in Index, EU27 = 100":
        "Η αγοραστική πίεση για την Ελλάδα έναντι της διάμεσης τιμής της ΕΕ "
        "και κάθε άλλης χώρας, σε δείκτη με ΕΕ27 = 100",
    "Wage-adjusted affordability for Greece against the EU median and every "
    "other country, in Index, EU27 = 100, higher = worse":
        "Η αγοραστική πίεση για την Ελλάδα έναντι της διάμεσης τιμής της ΕΕ "
        "και κάθε άλλης χώρας, σε δείκτη με ΕΕ27 = 100, όσο πιο ψηλά τόσο "
        "χειρότερα",
    "Accumulated unemployment for all 27 countries, latest year, in "
    "percentage-point-years above 2009":
        "Η συσσωρευμένη ανεργία και για τις 27 χώρες, τελευταίο έτος, σε "
        "μονάδες-έτη πάνω από το 2009",
    "Years wages below 2008 for all 27 countries, latest year, in "
    "consecutive years below the 2008 level":
        "Τα χρόνια με μισθούς κάτω από το 2008 και για τις 27 χώρες, τελευταίο "
        "έτος, σε συνεχόμενα χρόνια κάτω από το επίπεδο του 2008",
    "Housing deterioration since 2010 for all 27 countries, latest year, in "
    "percentage-point-years above 2010":
        "Η συσσωρευμένη επιβάρυνση από το κόστος στέγασης από το 2010, και για τις 27 χώρες, τελευταίο "
        "έτος, σε μονάδες-έτη πάνω από το 2010",
    "Standardised between-country against within-country estimates for every "
    "accumulated measure":
        "Τυποποιημένες εκτιμήσεις μεταξύ χωρών έναντι εκτιμήσεων εντός χωρών, "
        "για κάθε συσσωρευμένο δείκτη",
    "Country residuals under both specifications, on identical rows":
        "Τα ανεξήγητα υπόλοιπα των χωρών και στις δύο εκδοχές του μοντέλου, "
        "πάνω στις ίδιες ακριβώς γραμμές δεδομένων",
}

# ---------------------------------------------------------------------------
# The always-visible "what this shows" line under each figure's badge and
# question -- what it measures, how, and over what period/unit, so a reader
# who only screens one chart still has enough to follow it. Translated
# wholesale rather than phrase by phrase, same as CAVEATS below: these are
# short authored sentences, not a vocabulary of recurring fragments.
# ---------------------------------------------------------------------------
DEFINITIONS = {
    "F1":
        "AROP: ποσοστό ατόμων με εισόδημα κάτω από το 60% του εθνικού "
        "διάμεσου εισοδήματος, υπολογιζόμενο εκ νέου κάθε χρόνο. Δηλωμένη "
        "δυσκολία: ποσοστό νοικοκυριών που δηλώνουν ότι τα βγάζουν πέρα «με "
        "δυσκολία» ή «με μεγάλη δυσκολία». Και τα δύο από την EU-SILC, "
        "2015–2024.",
    "F3":
        "Το όριο φτώχειας του AROP, υπολογιζόμενο εκ νέου κάθε χρόνο, "
        "έναντι του ίδιου ορίου σταθεροποιημένου στην πραγματική του αξία "
        "του 2008. Ποσοστό ατόμων κάτω από κάθε όριο, και η ίδια η αξία "
        "του ορίου. EU-SILC, 2003–2025.",
    "F5":
        "Ο AROPE και τα τρία συστατικά του (εισοδηματική φτώχεια, υλική "
        "στέρηση, πολύ χαμηλή ένταση εργασίας), ανά ηλικιακή ομάδα και "
        "φύλο. Ποσοστό ατόμων. EU-SILC, 2015–2024.",
    "F7":
        "Ποσοστό του χάσματος Ελλάδας–διάμεσης τιμής ΕΕ του 2015 που "
        "έκλεισε κάθε δείκτης μέχρι το 2024 (0 = καμία μεταβολή, 1 = "
        "πλήρες κλείσιμο, αρνητικό = διεύρυνση). EU-SILC και εθνικοί "
        "λογαριασμοί της Eurostat.",
    "F8":
        "Η δηλωμένη δυσκολία έναντι τεσσάρων δεικτών υλικής δυσκολίας "
        "(απρόοπτο έξοδο, υλική στέρηση, θέρμανση, καθυστερήσεις "
        "πληρωμών), ο καθένας ως απόκλιση από τον δικό του μέσο όρο "
        "2015–2024. EU-SILC.",
    "F10":
        "Μακροχρόνια ανεργία (% του εργατικού δυναμικού), υλικοί πόροι "
        "(πραγματική ατομική κατανάλωση ανά κάτοικο, σε ΜΑΔ), και "
        "αγοραστική πίεση (δείκτης, ΕΕ=100), Ελλάδα έναντι της διάμεσης "
        "χώρας της ΕΕ, τελευταίο έτος.",
    "F11":
        "Η σωρευτική υπέρβαση κάθε χώρας πάνω από τη δική της βάση πριν "
        "την κρίση, αθροισμένη έτος με έτος από την έναρξη της κρίσης. "
        "Μονάδες-έτη ή έτη, και οι 27 χώρες της ΕΕ.",
    "F14":
        "Το ανεξήγητο υπόλοιπο της Ελλάδας εκτός δείγματος (δηλωμένη "
        "δυσκολία μείον πρόβλεψη μοντέλου, σε ποσοστιαίες μονάδες) σε δύο "
        "διαφορετικές, εξίσου υποστηρίξιμες εξειδικεύσεις μοντέλου, και η "
        "θέση της στην ΕΕ σε καθεμία.",
    "F21":
        "Αριθμός δεικτών στους οποίους η Ελλάδα βρίσκεται στο χειρότερο "
        "πέμπτο των χωρών της ΕΕ, ανά έτος. EU-SILC και εθνικοί "
        "λογαριασμοί της Eurostat, 2015–2024.",
}

# ---------------------------------------------------------------------------
# The methods-and-limits note under each figure. These stay technical, as
# they do in English: they sit inside a collapsed <details>, which is where
# the editorial standard says this material belongs.
# ---------------------------------------------------------------------------
CAVEATS = {
    "F1":
        "Πρόκειται για σύγκριση δύο επίσημων δεικτών. Η οικονομική δυσκολία "
        "μετριέται σε ΝΟΙΚΟΚΥΡΙΑ, ενώ η εισοδηματική φτώχεια σε ΑΤΟΜΑ, γι' "
        "αυτό ο άξονας αναφέρεται γενικά σε «ποσοστό». Στη δεύτερη καρτέλα, "
        "η γραμμή προσαρμογής (γκρι διακεκομμένη) υπολογίζεται χωρίς την "
        "Ελλάδα: περιγράφει το ευρωπαϊκό μοτίβο με το οποίο συγκρίνεται η "
        "χώρα και όχι μια σχέση στη διαμόρφωση της οποίας συμμετέχει η ίδια. "
        "Το σημείο αναφοράς αντιστοιχεί στη διάμεση χώρα κάθε δείκτη "
        "ΞΕΧΩΡΙΣΤΑ και επομένως δεν αναπαριστά απαραίτητα κάποια πραγματική "
        "χώρα. Και οι δύο καρτέλες αφορούν συγκεντρωτικά στοιχεία χώρας και "
        "δεν επιτρέπουν συμπεράσματα για μεμονωμένα νοικοκυριά.",
    "F8":
        "Πρόκειται για επιβεβαίωση από την ίδια έρευνα, όχι για ανεξάρτητη "
        "επικύρωση ή αιτιώδη απόδειξη. Οι ελληνικές συσχετίσεις με την "
        "οικονομική δυσκολία είναι: απρόοπτα έξοδα 0,92 · υλική στέρηση 0,94 "
        "· θέρμανση του σπιτιού 0,87 · καθυστερήσεις σε λογαριασμούς 0,37. "
        "Κάθε γραμμή δείχνει την απόκλιση από τον δικό της μέσο όρο της "
        "περιόδου 2015-2024, μαζί με την αντίστοιχη ευρωπαϊκή διάμεση τιμή, "
        "ώστε σειρές με διαφορετικές κλίμακες να μπορούν να παρουσιαστούν "
        "στον ίδιο άξονα. Συγκρίνονται επομένως οι μεταβολές και όχι τα "
        "απόλυτα επίπεδα. Η κλίμακα είναι κοινή και στις τέσσερις καρτέλες. "
        "Η ευρωπαϊκή διάμεση οικονομική δυσκολία δεν εμφανίζεται σκόπιμα, "
        "επειδή το ερώτημα εδώ είναι αν οι συγκεκριμένες ελληνικές "
        "δυσκολίες κινούνται μαζί με τις ελληνικές απαντήσεις.",
    "F21":
        "Το γράφημα συνοψίζει περιγραφικά την έκταση του ελληνικού "
        "μειονεκτήματος. Δεν δείχνει ότι η εξάπλωση των προβλημάτων είναι "
        "από μόνη της παράγοντας που εξηγεί την οικονομική δυσκολία. Όταν "
        "αυτό εξετάστηκε στατιστικά, η σχέση δεν αποδείχθηκε σταθερή: από "
        "μόνη της δεν πέρασε το προκαθορισμένο όριο (p = 0,12), ενώ μετά "
        "την προσθήκη των υπόλοιπων συσσωρευμένων δεικτών στο μοντέλο το "
        "πρόσημό της αντιστράφηκε. Επομένως, εδώ χρησιμοποιείται μόνο για "
        "να περιγράψει πόσο ευρύ είναι το ελληνικό μειονέκτημα, όχι για να "
        "το εξηγήσει. Το σύνολο είναι σταθερό και περιλαμβάνει 16 δείκτες "
        "για τους οποίους υπάρχει έγκυρη ευρωπαϊκή κατάταξη τόσο το 2008 "
        "όσο και το 2024. Οι δείκτες επιλέχθηκαν χωρίς να ληφθεί υπόψη αν η "
        "θέση της Ελλάδας βελτιώθηκε ή χειροτέρεψε, ώστε να συγκρίνονται τα "
        "ίδια χαρακτηριστικά σε όλη την περίοδο. Η ανεργία, η ανεργία των "
        "νέων και το ποσοστό απασχόλησης δεν περιλαμβάνονται, επειδή "
        "συγκρίσιμα ευρωπαϊκά δεδομένα γι' αυτούς υπάρχουν μόνο από το "
        "2009. Περιλαμβάνονται όμως άλλοι βασικοί δείκτες της αγοράς "
        "εργασίας, όπως οι ώρες εργασίας, η ωριαία αμοιβή, η ένταση "
        "εργασίας και οι πραγματικοί μισθοί. "
        '<a href="statistical_appendix.html#p_breadth_fixed_basket">Το '
        "παράρτημα</a> δείχνει και το ευρύτερο σύνολο υποψήφιων δεικτών "
        "(στα αγγλικά). Ο ίδιος ο δείκτης οικονομικής δυσκολίας και οι "
        "μεταβλητές που χρησιμοποιούνται ως έλεγχοι στα μοντέλα έχουν "
        "επίσης εξαιρεθεί. Στην καρτέλα «Ποιοι δείκτες», ο άξονας δείχνει "
        "σχετική θέση και όχι την αρχική τιμή κάθε δείκτη: το 0 αντιστοιχεί "
        "στην καλύτερη θέση μεταξύ των χωρών της ΕΕ και το 100 στη "
        "χειρότερη. Έτσι μπορούν να παρουσιαστούν στον ίδιο άξονα δείκτες "
        "με διαφορετικές μονάδες μέτρησης και διαφορετική κατεύθυνση ως "
        "προς το τι θεωρείται δυσμενές. Στην καρτέλα «Πόσοι δείκτες», η "
        "«διάμεση τιμή των χωρών της ΕΕ» είναι η διάμεσος, μεταξύ των "
        "κρατών-μελών, του ποσοστού των 16 δεικτών στους οποίους κάθε χώρα "
        "βρίσκεται στο χειρότερο πέμπτο της Ένωσης. Δεν πρόκειται δηλαδή "
        "για πληθυσμιακά σταθμισμένο ευρωπαϊκό δείκτη. Η Κροατία δεν "
        "εμφανίζεται ως γραμμή, επειδή δεν διαθέτει πλήρη στοιχεία και για "
        "τους 16 δείκτες σε καμία χρονιά της περιόδου.",
    "F3":
        "Η εκτίμηση της φτώχειας με σταθερό όριο είναι μια προσέγγιση που "
        "κατασκευάστηκε για αυτή την ανάλυση και σημειώνεται ως τέτοια όπου "
        "εμφανίζεται. Η πρώτη καρτέλα μετρά ΑΤΟΜΑ, ενώ η δεύτερη ΕΥΡΩ. Στη "
        "δεύτερη καρτέλα, οι δύο γραμμές αφορούν το ίδιο επίσημο όριο "
        "φτώχειας: η μία το δείχνει όπως δημοσιεύτηκε, σε τρέχοντα ευρώ "
        "κάθε χρονιάς, ενώ η άλλη δείχνει την αξία του σε σταθερές τιμές "
        "του 2008, δηλαδή τι μπορούσε πραγματικά να αγοράσει. Σε τρέχοντα "
        "ευρώ το όριο ανακάμπτει· σε πραγματικούς όρους όχι. Αυτή η διαφορά "
        "εξηγεί γιατί στην πρώτη καρτέλα ο επίσημος δείκτης φτώχειας και η "
        "εκτίμηση με σταθερό όριο ακολουθούν τόσο διαφορετική πορεία. Και "
        "οι δύο καρτέλες αφορούν αποκλειστικά την Ελλάδα και δεν "
        "χρησιμοποιούνται για συγκρίσεις μεταξύ χωρών.",
    "F5":
        "Πρόκειται για μεταβολές σε ποσοστά ομάδων, όχι για στοιχεία που "
        "παρακολουθούν τα ίδια άτομα στον χρόνο. Η εθνική αύξηση του "
        "2024-2025 οφείλεται κυρίως σε μεταβολές μέσα στις ομάδες, ιδίως σε "
        "επιδείνωση για τους άνω των 65, και όχι στη γήρανση του πληθυσμού. "
        "Τα συστατικά του AROPE αποτελούν ΕΝΩΣΗ συνόλων και δεν αθροίζονται. "
        "Η πολύ χαμηλή ένταση εργασίας είναι μέρος του AROPE, αλλά δεν "
        "υπάρχουν συγκρίσιμα εθνικά δεδομένα για την καρτέλα των συστατικών· η "
        "διαθέσιμη ηλικιακή κάλυψη χρησιμοποιεί διαφορετική πληθυσμιακή βάση, "
        "και σε κάθε περίπτωση τα συγκεντρωτικά ποσοστά των συστατικών δεν "
        "μπορούν να ανασυνθέσουν την ένωση του AROPE. Και στις τέσσερις "
        "καρτέλες το χρώμα δείχνει τον δείκτη ή την ομάδα και η διακεκομμένη "
        "γραμμή τη χώρα, οπότε κάθε ελληνική γραμμή είναι ζευγαρωμένη με τη "
        "διάμεση τιμή της ΕΕ για το ίδιο πράγμα στο ίδιο χρώμα. Οι καρτέλες "
        "ανά συστατικό, με κάθε άλλο κράτος-μέλος σχεδιασμένο από πίσω, "
        "βρίσκονται στο στατιστικό παράρτημα.",
    "F7":
        "ΕΝΑ ΧΑΣΜΑ ΠΟΥ ΣΤΕΝΕΥΕΙ ΔΕΝ ΣΗΜΑΙΝΕΙ ΟΤΙ Η ΕΛΛΑΔΑ ΒΕΛΤΙΩΘΗΚΕ. Μπορεί "
        "να στενεύει είτε επειδή βελτιώθηκε η Ελλάδα, είτε επειδή χειροτέρεψε "
        "η υπόλοιπη ΕΕ είτε επειδή και οι δύο κινήθηκαν προς την ίδια "
        "κατεύθυνση με διαφορετική ταχύτητα. Το γράφημα αποτυπώνει ΣΧΕΤΙΚΗ "
        "ΣΥΓΚΛΙΣΗ, όχι εθνική ανάκαμψη. Γι' αυτό οι αρχικές και τελικές τιμές "
        "τόσο της Ελλάδας όσο και της διάμεσης χώρας της ΕΕ εμφανίζονται "
        "στην ένδειξη και στον συνοδευτικό πίνακα. Το «έκλεισε το 71% του "
        "χάσματος» και το «οι συνθήκες βελτιώθηκαν κατά 71%» είναι εντελώς "
        "διαφορετικοί ισχυρισμοί. Ο άξονας είναι χωρίς μονάδα, επειδή τα "
        "επιμέρους χάσματα εκφράζονται σε διαφορετικές μονάδες: ποσοστιαίες "
        "μονάδες, μονάδες δείκτη και Μονάδες Αγοραστικής Δύναμης (ΜΑΔ) ανά "
        "άτομο.",
    "F11":
        "Οι σχέσεις είναι συσχετίσεις μεταξύ χωρών. Δεν τεκμηριώνουν "
        "δυναμική εντός της Ελλάδας ούτε αιτιώδη επίδραση, ενώ οι σημερινές "
        "συνθήκες λαμβάνονται υπόψη στους σχετικούς ελέγχους. Οι τρεις "
        "σωρευτικοί δείκτες έχουν διαφορετικές μονάδες και δεν συγκρίνονται "
        "αριθμητικά μεταξύ τους: η συσσωρευμένη ανεργία και η επιδείνωση "
        "της στέγασης μετρώνται σε μονάδες-έτη, ενώ η μη ανάκαμψη των "
        "μισθών σε συνεχόμενα χρόνια.",
    "F13A":
        "Το γράφημα συγκρίνει δύο διαφορετικούς τύπους σχέσης. Η σύγκριση "
        "μεταξύ χωρών εξετάζει αν οι χώρες με μεγαλύτερο συσσωρευμένο "
        "βάρος δηλώνουν και μεγαλύτερη οικονομική δυσκολία. Η ενδοχωρική "
        "σύγκριση εξετάζει αν, μέσα στην ίδια χώρα, η δυσκολία μεταβάλλεται "
        "καθώς μεταβάλλεται το συσσωρευμένο βάρος. Το δεύτερο ερώτημα είναι "
        "δυσκολότερο να απαντηθεί, επειδή βασίζεται σε περίπου μία δεκαετία "
        "ετήσιων παρατηρήσεων ανά χώρα και σε σχετικά περιορισμένη "
        "μεταβολή μέσα στην ίδια χώρα. Γι' αυτό οι ενδοχωρικές εκτιμήσεις "
        "είναι πολύ πιο αβέβαιες. Η έλλειψη καθαρού ενδοχωρικού "
        "αποτελέσματος δεν αναιρεί τη σχέση μεταξύ χωρών· δείχνει ότι τα "
        "διαθέσιμα δεδομένα δεν επαρκούν για να τεκμηριώσουν την ίδια "
        "σχέση μέσα στις χώρες στον χρόνο.",
    "F14":
        "Καμία από τις δύο εκδοχές δεν αντιμετωπίζεται ως οριστική. Η μία "
        "αξιοποιεί περισσότερη πληροφορία για τις πραγματικές στερήσεις "
        "των νοικοκυριών, αλλά αυτή η πληροφορία προέρχεται από το ίδιο "
        "εργαλείο μέτρησης. Η άλλη διατηρεί μεγαλύτερη ανεξαρτησία ανάμεσα "
        "στους δείκτες, αλλά αφήνει έξω ακριβώς εκείνες τις στερήσεις που "
        "συνδέονται πιο στενά με την οικονομική δυσκολία.",
}

# One lookup for every exact-match string the localizer replaces.
STRINGS = {}
for _d in (COUNTRIES, TABS, LABELS, CHROME, HEADERS, QUESTIONS, ALT):
    STRINGS.update(_d)

# Strings that are legitimately left as they are: pure numbers (years, age
# bands) and the CSS tone names the chart JS reads as class fragments.
KEEP_AS_IS = {"18-24", "25-49", "50-64", "chart-gr", "chart-neutral",
              "chart-eu", "chart-warn", "chart-s4"}


# ---------------------------------------------------------------------------
# Hover tooltips. chart_engine builds these from a template, so they are
# translated as parts rather than as 146 whole strings: DETAIL_RULES handles
# the number-bearing sentences, DETAIL_NAMES the indicator names and units.
# ---------------------------------------------------------------------------
DETAIL_NAMES = {
    # indicator names, as the tooltip spells them out
    "Real household disposable income (2008 = 100)":
        "Πραγματικό διαθέσιμο εισόδημα νοικοκυριών (2008 = 100)",
    "Real wages, compensation per employee (own 2008 = 100)":
        "Πραγματικοί μισθοί, αμοιβή ανά εργαζόμενο (2008 = 100)",
    "Real AROP poverty threshold (own 2008 = 100)":
        "Πραγματικό όριο φτώχειας AROP (2008 = 100)",
    "Real household consumption per capita":
        "Πραγματική κατανάλωση νοικοκυριών ανά άτομο",
    "Real GDP per capita": "Πραγματικό ΑΕΠ ανά άτομο",
    "Compensation per hour worked (PPS)": "Αμοιβή ανά ώρα εργασίας (ΜΑΔ)",
    "Actual weekly working hours (main job)":
        "Πραγματικές εβδομαδιαίες ώρες εργασίας (κύρια απασχόληση)",
    "Work-effort squeeze (hours vs hourly pay, EU = 100)":
        "Πίεση έντασης εργασίας (ώρες έναντι ωριαίας αμοιβής, ΕΕ = 100)",
    "Wage-adjusted price pressure — Overall household consumption":
        "Πίεση τιμών σε σχέση με τις αμοιβές, συνολική κατανάλωση νοικοκυριών",
    "Cannot keep home adequately warm": "Αδυναμία επαρκούς θέρμανσης του σπιτιού",
    "Net migration of nationals (per 1,000 population)":
        "Καθαρή μετανάστευση ημεδαπών (ανά 1.000 κατοίκους)",
    "per 1,000 people": "ανά 1.000 άτομα",
    "Household financial expectations, next 12 months":
        "Οικονομικές προσδοκίες νοικοκυριών, επόμενοι 12 μήνες",
    "Income inequality (S80/S20 ratio)": "Εισοδηματική ανισότητα (λόγος S80/S20)",
    "HICP inflation, headline": "Πληθωρισμός ΕνΔΤΚ, γενικός δείκτης",
    "HICP inflation, housing & energy": "Πληθωρισμός ΕνΔΤΚ, στέγαση και ενέργεια",
    "HICP inflation, food & non-alcoholic beverages":
        "Πληθωρισμός ΕνΔΤΚ, τρόφιμα και μη αλκοολούχα ποτά",
    # units
    "chain-linked EUR": "ευρώ σε σταθερές τιμές",
    "ratio": "λόγος",
    "PPS per hour": "ΜΑΔ ανά ώρα",
    "hours/week": "ώρες/εβδομάδα",
    "balance (net %)": "ισοζύγιο (καθαρό %)",
    "% annual change": "% ετήσια μεταβολή",
    "percentage points": "ποσοστιαίες μονάδες",
    "index, EU=100": "δείκτης, ΕΕ=100",
    "index, EU = 100": "δείκτης, ΕΕ = 100",
    "index points, EU = 100": "μονάδες δείκτη, ΕΕ = 100",
    "index, 2008=100": "δείκτης, 2008=100",
    "index points, 2008 = 100": "μονάδες δείκτη, 2008 = 100",
    # the lede sentence some figures print above their table
    # split by a <b> mid-sentence, so it arrives as two text nodes
    "Of 16 indicators,": "Από τους 16 δείκτες,",
    "4 were already in the EU's worst fifth in 2008, 7 entered it by 2024, "
    "and none left":
        "οι 4 ήταν ήδη στο χειρότερο πέμπτο της ΕΕ το 2008, οι 7 μπήκαν ως "
        "το 2024, και κανένας δεν βγήκε",
    # right-hand row labels and band shading
    "no dynamic support": "χωρίς μεταβολή",
    "EU's worst fifth": "χειρότερο πέμπτο της ΕΕ",
}
STRINGS.update(DETAIL_NAMES)

# (pattern, replacement) applied in order to tooltip text. The numbers are
# captured and put back, so only the words are translated.
DETAIL_RULES = [
    (r"\brank (\S+) of (\S+)", r"θέση \1 από \2"),
    (r"\bpercentage-point-years above (\S+)", r"μονάδες-έτη πάνω από το \1"),
    (r"\b(\d{4}): position (\S+) of (\S+)", r"\1: θέση \2 στα \3"),
    (r"\bfrozen (\S+) &rarr; companion (\S+)", r"βασικό \1 &rarr; εναλλακτικό \2"),
    (r"\bconsecutive years below the (\S+) level",
     r"συνεχόμενα χρόνια κάτω από το επίπεδο του \1"),
    (r"\bsame side of zero", "ίδια πλευρά του μηδενός"),
    (r"\bcrosses zero", "περνά το μηδέν"),
    (r"(\S+) is the best place in the Union to be on this indicator, (\S+) the worst",
     r"\1 είναι η καλύτερη θέση στην Ένωση για αυτόν τον δείκτη, \2 η χειρότερη"),
    (r"\bGreece (\S+) &rarr; (\S+)", r"Ελλάδα \1 &rarr; \2"),
    (r"\bEU median (\S+) &rarr; (\S+)", r"διάμεση τιμή ΕΕ \1 &rarr; \2"),
    (r"\bgap (\S+) &rarr; (\S+)", r"χάσμα \1 &rarr; \2"),
    (r"\bbetween (\S+) SD \(p (\S+)\)", r"μεταξύ χωρών \1 τ.α. (p \2)"),
    (r"\bwithin (\S+) SD \(p (\S+)\)", r"εντός χωρών \1 τ.α. (p \2)"),
    (r"\braw: between (\S+) within (\S+)", r"ακατέργαστα: μεταξύ \1 εντός \2"),
    (r"\bfirst difference (\S+) \(p (\S+)\)", r"πρώτη διαφορά \1 (p \2)"),
    (r"(\S+) of the initial gap closed", r"\1 του αρχικού χάσματος έκλεισε"),
    (r"\bgap widened by (\S+) of its (\S+) size",
     r"το χάσμα διευρύνθηκε κατά \1 του μεγέθους του το \2"),
    (r"\boutside the worst fifth in both years",
     "εκτός του χειρότερου πέμπτου και τις δύο χρονιές"),
    (r"\bentered worst fifth", "μπήκε στο χειρότερο πέμπτο"),
    # the tooltip puts <b> mid-sentence, so these also arrive alone
    (r"\bSD\b", "τ.α."),
    (r"\bbetween\b", "μεταξύ χωρών"),
    (r"\bwithin\b", "εντός χωρών"),
    (r"\balready worst fifth", "ήδη στο χειρότερο πέμπτο"),
]

# Latin fragments that legitimately survive translation: measure acronyms and
# statistical shorthand that Greek publications keep in Latin script.
DETAIL_ALLOWED = ("PPS", "EU", "AROP", "AROPE", "SD", "HICP", "GDP", "S80",
                  "S20", "p ", "opacity", "span", "style", "br", "b")
