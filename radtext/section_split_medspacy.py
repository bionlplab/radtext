import bioc
import medspacy

from radtext.core import BioCProcessor
from radtext.section_split_regex import strip, is_empty


class BioCSectionSplitterMedSpacy(BioCProcessor):
    def __init__(self, nlp):
        self.nlp = nlp

    def process_document(self, doc: bioc.BioCDocument) -> bioc.BioCDocument:
        """
        Split one report into sections. Section splitting is a deterministic
        consequence of section titles.
        """
        def create_passage(text, offset, start, end, title=None):
            passage = bioc.BioCPassage()
            passage.offset = start + offset
            passage.text = text[start:end]
            if title is not None:
                passage.infons['section_concept'] = title[:-1].strip() if title[-1] == ':' else title.strip()
                passage.infons['type'] = 'title_1'
            strip(passage)
            return passage

        offset, text = bioc.utils.get_text(doc)
        del doc.passages[:]

        medspacy_doc = self.nlp(text)
        for title in medspacy_doc._.section_titles:
            if len(title) == 0:
                continue
            passage = create_passage(text, offset, title.start_char, title.end_char, title.text)
            if not is_empty(passage):
                doc.add_passage(passage)

        for body in medspacy_doc._.section_bodies:
            passage = create_passage(text, offset, body.start_char, body.end_char)
            if not is_empty(passage):
                doc.add_passage(passage)

        doc.passages = sorted(doc.passages, key=lambda p: p.offset)
        return doc


if __name__ == '__main__':
    text = r"""Admission Date:  [**2118-6-2**]       Discharge Date:  [**2118-6-14**]

Date of Birth:                    Sex:  F

Service:  MICU and then to [**Doctor Last Name **] Medicine

HISTORY OF PRESENT ILLNESS:  This is an 81-year-old female
with a history of emphysema (not on home O2), who presents
with three days of shortness of breath thought by her primary
care doctor to be a COPD flare.  Two days prior to admission,
she was started on a prednisone taper and one day prior to
admission she required oxygen at home in order to maintain
oxygen saturation greater than 90%.  She has also been on
levofloxacin and nebulizers, and was not getting better, and
presented to the [**Hospital1 18**] Emergency Room.

In the [**Hospital3 **] Emergency Room, her oxygen saturation was
100% on CPAP.  She was not able to be weaned off of this
despite nebulizer treatment and Solu-Medrol 125 mg IV x2.

Review of systems is negative for the following:  Fevers,
chills, nausea, vomiting, night sweats, change in weight,
gastrointestinal complaints, neurologic changes, rashes,
palpitations, orthopnea.  Is positive for the following:
Chest pressure occasionally with shortness of breath with
exertion, some shortness of breath that is positionally
related, but is improved with nebulizer treatment.

PAST MEDICAL HISTORY:
1. COPD.  Last pulmonary function tests in [**2117-11-3**]
demonstrated a FVC of 52% of predicted, a FEV1 of 54% of
predicted, a MMF of 23% of predicted, and a FEV1:FVC ratio of
67% of predicted, that does not improve with bronchodilator
treatment.  The FVC, however, does significantly improve with
bronchodilator treatment consistent with her known reversible
air flow obstruction in addition to an underlying restrictive
ventilatory defect.  The patient has never been on home
oxygen prior to this recent episode.  She has never been on
steroid taper or been intubated in the past.
2. Lacunar CVA.  MRI of the head in [**2114-11-4**]
demonstrates "mild degree of multiple small foci of high T2
signal within the white matter of both cerebral hemispheres
as well as the pons, in the latter region predominantly to
the right of midline.  The abnormalities, while nonspecific
in etiology, are most likely secondary to chronic
microvascular infarction.  There is no mass, lesion, shift of
the normal midline strictures or hydrocephalus.  The major
vascular flow patterns are preserved.  There is moderate
right maxillary, moderate bilateral ethmoid, mild left
maxillary, minimal right sphenoid, and frontal sinus mucosal
thickening.  These abnormalities could represent an allergic
or some other type of inflammatory process.  Additionally
noted is a moderately enlarged subtotally empty sella
turcica".
3. Angina:  Most recent stress test was in [**2118-1-3**]
going for four minutes with a rate pressure product of
10,000, 64% of maximum predicted heart rate without evidence
of ischemic EKG changes or symptoms.  The imaging portion of
the study demonstrated no evidence of myocardial ischemia and
a calculated ejection fraction of 84%.  The patient denies
angina at rest and gets angina with walking a few blocks.
Are alleviated by sublingual nitroglycerin.
4. Hypothyroidism on Synthroid.
5. Depression on Lexapro.
6. Motor vehicle accident with head injury approximately 10
years ago.

MEDICATIONS ON ADMISSION:
1. Hydrochlorothiazide 25 q.d.
2. Prednisone 60 mg, 50 mg, 40 mg, 20 mg.
3. Levofloxacin 500 mg q.d.
4. Imdur 60 mg q.d.
5. Synthroid 75 mcg q.d.
6. Pulmicort nebulizer b.i.d.
7. Albuterol nebulizer q.4. prn.
8. Lexapro 10 mg q.d.
9. Protonix 40 mg q.d.
10. Aspirin 81 mg q.d.

ALLERGIES:  Norvasc leads to lightheadedness and headache.

FAMILY HISTORY:  Noncontributory.

SOCIAL HISTORY:  Lives with her husband, Dr. [**Known lastname 1809**] an
eminent Pediatric Neurologist at [**Hospital3 1810**].  The
patient is a prior smoker, but has not smoked in over 10
years.  She has no known alcohol use and she is a full code.

PHYSICAL EXAM AT TIME OF ADMISSION:  Blood pressure 142/76,
heart rate 100 and regular, respirations at 17-21, and 97%
axillary temperature.  She was saturating at 100% on CPAP
with dry mucous membranes.  An elderly female in no apparent
distress.  Pupils are equal, round, and reactive to light and
accommodation.  Extraocular movements are intact.  Oropharynx
difficult to assess due to CPAP machine.  No evidence of
jugular venous pressure, however, the strap from the CPAP
machine obscures the neck exam.  Cranial nerves II through
XII are grossly intact.  Neck is supple without
lymphadenopathy.  Heart exam:  Tachycardic, regular, obscured
by loud bilateral wheezing with increase in the expiratory
phase as well as profuse scattered rhonchi throughout the
lung fields.  Positive bowel sounds, soft, nontender,
nondistended, obese, no masses.  Mild edema of the lower
extremities without clubbing or cyanosis, no rashes.  There
is a right hand hematoma.  Strength is assessed as [**5-9**] in the
lower extremities, [**5-9**] in the upper extremities with a normal
mental status and cognition.

LABORATORY STUDIES:  White count 19, hematocrit 41, platelets
300.  Chem-7:  127, 3.6, 88, 29, 17, 0.6, 143.  Troponin was
negative.  CKs were negative times three.  Initial blood gas
showed a pH of 7.4, pO2 of 66, pCO2 of 54.

Chest x-ray demonstrates a moderate sized hiatal hernia,
segmental atelectasis, left lower lobe infiltrate versus
segmental atelectasis.

EKG shows normal sinus rhythm at 113 beats per minute, normal
axis, no evidence of ST-T wave changes.

BRIEF SUMMARY OF HOSPITAL COURSE:
1. COPD/dyspnea/pneumonia:  The patient was initially placed
on an aggressive steroid taper and admitted to the Medical
Intensive Care Unit due to her difficulty with oxygenation
despite CPAP machine.  She was also given nebulizer
treatments q.4h. as well as chest PT.  The nebulizers were
increased to q.1h. due to the fact that she continued to have
labored breathing.

Due to persistent respiratory failure and labored breathing,
the patient was intubated on [**2118-6-7**] in order to improve
oxygenation, ventilation, and ability to suction.  A
bronchoscopy was performed on [**2118-6-7**], which demonstrated
marked narrowing of the airways with expiration consistent
with tracheomalacia.

On [**2118-6-9**], two silicone stents were placed, one in the left
main stem (12 x 25 and one in the trachea 16 x 40) by Dr.
[**First Name (STitle) **] [**Name (STitle) **] under rigid bronchoscopy with general anesthesia.

On [**2118-6-11**], the patient was extubated to a cool mist shovel
mask and her oxygen was titrated down to 2 liters nasal
cannula at which time she was transferred to the medical
floor.  On the medical floor, the steroids were weaned to off
on [**2118-6-14**], and the patient was saturating at 97% on 2
liters, 92% on room air.

On [**2118-6-14**], the patient was seen again by the Interventional
Pulmonology service, who agreed that she looked much improved
and recommended that she go to pulmonary rehabilitation with
followup within six weeks' time status post placement of
stents in respiratory failure.

2. Cardiovascular:  The patient was ruled out for a MI.  She
did have another episode on the medical floor of chest pain,
which showed no evidence of EKG changes and negative
troponin, negative CKs x3.  She was continued on aspirin,
Imdur, and diltiazem for rate control per her outpatient
regimen.

3. Hypertension:  She was maintained on diltiazem and
hydrochlorothiazide with adequate blood pressure control and
normalization of electrolytes.

4. Hematuria:  The patient had intermittent hematuria likely
secondary to Foley placement.  The Foley catheter was
discontinued on [**2118-6-14**].  She had serial urinalyses, which
were all negative for signs of infection.

5. Hyperglycemia:  Patient was placed on insulin-sliding
scale due to hyperglycemia, which was steroid induced.  This
worked quite well and her glucose came back to normal levels
once the steroids were tapered to off.

6. Leukocytosis:  Patient did have a profound leukocytosis of
20 to 22 during much of her hospital course.  As the steroids
were tapered to off, her white blood cell count on [**2118-6-14**]
was 15,000.  It was felt that the leukocytosis was secondary
to both steroids as well as question of a left lower lobe
pneumonia.

7. For the left lower lobe pneumonia, the patient had
initially received a course of levofloxacin 500 p.o. q.d.
from [**2118-6-4**] to [**2118-6-10**].  This was restarted on [**2118-6-12**]
for an additional seven day course given the fact that she
still had the leukocytosis and still had marked rales at the
left lower lobe.

8. Hypothyroidism:  The patient was continued on outpatient
medical regimen.

9. Depression:  The patient was continued on Lexapro per
outpatient regimen.  It is recommended that she follow up
with a therapist as an outpatient due to the fact that she
did have a blunted affect throughout much of the hospital
course, and did appear clinically to be depressed.

10. Prophylaxis:  She was maintained on proton-pump inhibitor
with subQ Heparin.

11. Sore throat:  The patient did have a sore throat for much
of the hospital course post extubation.  This was treated
with Cepacol lozenges as well as KBL liquid (a solution
containing Kaopectate, Bismuth, and lidocaine) at bedtime.

12. Communication/code status:  The patient was full code
throughout her hospital course, and communication was
maintained with the patient and her husband.

13. Muscle weakness:  The patient did have profound muscle
weakness and was evaluated by Physical Therapy, and was found
to have impaired functional mobility, impaired
musculoskeletal performance, impaired gas exchange, impaired
endurance, impaired ventilation, and needed help with supine
to sit.  However, she was able to tolerate sitting in a chair
for approximately one hour.

On motor exam, her flexors and extensors of the lower
extremities were [**4-8**] at the knee, [**4-8**] at the ankle, [**4-8**] at
the elbows, and [**4-8**] hips.  It was felt that this weakness was
most likely due to a combination of steroid myopathy as well
as muscle atrophy secondary to deconditioning after a
prolonged hospital course.

14. Speech/swallow:  The patient had a Speech and Swallow
evaluation showing no evidence of dysphagia, no evidence of
vocal cord damage status post tracheal stent placement.

DISCHARGE CONDITION:  The patient was able to oxygenate on
room air at 93% at the time of discharge.  She was profoundly
weak, but was no longer tachycardic and had a normal blood
pressure.  Her respirations were much improved albeit with
transmitted upper airway sounds.

DISCHARGE STATUS:  The patient will be discharged to [**Hospital1 **]
for both pulmonary and physical rehabilitation.

DISCHARGE MEDICATIONS:
1. Levothyroxine 75 mcg p.o. q.d.
2. Citalopram 10 mg p.o. q.d.
3. Aspirin 81 mg p.o. q.d.
4. Fluticasone 110 mcg two puffs inhaled b.i.d.
5. Salmeterol Diskus one inhalation b.i.d.
6. Acetaminophen 325-650 mg p.o. q.4-6h. prn.
7. Ipratropium bromide MDI two puffs inhaled q.2h. prn.
8. Albuterol 1-2 puffs inhaled q.2h. prn.
9. Zolpidem tartrate 5 mg p.o. q.h.s. prn.
10. Isosorbide dinitrate 10 mg p.o. t.i.d.
11. Diltiazem 60 mg p.o. q.i.d.
12. Pantoprazole 40 mg p.o. q.24h.
13. Trazodone 25 mg p.o. q.h.s. prn.
14. SubQ Heparin 5000 units subcutaneous b.i.d. until such
time that the patient is able to get out of bed twice a day.
15. Cepacol lozenges q.2h. prn.
16. Levofloxacin 500 mg p.o. q.d. for a seven day course to
be completed on [**2118-6-21**].
17. Kaopectate/Benadryl/lidocaine 5 mL p.o. b.i.d. prn, not
to be given around mealtimes for concern of dysphagia induced
by lidocaine.
18. Lorazepam 0.5-2 mg IV q.6h. prn.

FOLLOW-UP PLANS:  The patient is recommended to followup with
Dr. [**First Name4 (NamePattern1) **] [**Last Name (NamePattern1) 1407**], [**Telephone/Fax (1) 1408**] within two weeks of leaving
of the hospital.  She is also recommended to followup with
the Interventional Pulmonary service for followup status post
stent placement.  She is also recommended to followup with a
neurologist if her muscle weakness does not improve within
one week on physical therapy with concern for steroid-induced
myopathy.

FINAL DIAGNOSES:
1. Tracheomalacia status post tracheal and left main stem
bronchial stent placement.
2. Hypertension.
3. Hypothyroidism.
4. Restrictive lung defect.
5. Depression.


                     DR.[**Last Name (STitle) **],[**First Name3 (LF) **] 12-207


Dictated By:[**Last Name (NamePattern1) 1811**]
MEDQUIST36

D:  [**2118-6-14**]  11:30
T:  [**2118-6-14**]  11:33
JOB#:  [**Job Number 1812**]

    """
    nlp = medspacy.load(enable=["sectionizer"])
    sec_title = BioCSectionSplitterMedSpacy(nlp)
    doc = bioc.utils.as_document(text)
    doc = sec_title.process_document(doc)
    print(doc)
    # doc = nlp(text)
    # print(doc._.section_titles)
    # for s in doc._.section_spans:
    #     print(s.start_char)
    #
    # assert len(doc._.section_titles) == len(doc._.section_bodies)
    # for t, d in zip(doc._.section_titles, doc._.section_bodies):
    #     print(t.start_char, t.end_char, d.start_char, d.end_char)
    # print(doc._.section_spans)
