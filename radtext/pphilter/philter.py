import hashlib
import json
import os
import pickle
import re
import warnings
from pathlib import Path

import nltk

from radtext.pphilter.coordinate_map import CoordinateMap

# ucsf_include_tags = ['Date', 'Provider_Name', 'Phone_Fax', 'Patient_Name_or_Family_Member_Name',
#                      'Patient_Address', 'Provider_Address_or_Location',
#                      'Provider_Certificate_or_License', 'Patient_Medical_Record_Id',
#                      'Patient_Account_Number', 'Patient_Social_Security_Number',
#                      'Patient_Vehicle_or_Device_Id', 'Patient_Unique_Id', 'Procedure_or_Billing_Code',
#                      'Email', 'URL_IP', 'Patient_Biometric_Id_or_Face_Photo',
#                      'Patient_Certificate_or_License', 'Age']
# ucsf_patient_tags = ['Date', 'Phone_Fax', 'Age', 'Patient_Name_or_Family_Member_Name',
#                      'Patient_Address', 'Patient_Medical_Record_Id', 'Patient_Account_Number',
#                      'Patient_Social_Security_Number', 'Patient_Vehicle_or_Device_Id',
#                      'Patient_Unique_Id', 'Email', 'URL_IP', 'Patient_Biometric_Id_or_Face_Photo',
#                      'Patient_Certificate_or_License']
# ucsf_provider_tags = ['Provider_Name', 'Phone_Fax', 'Provider_Address_or_Location',
#                       'Provider_Certificate_or_License', 'Email', 'URL_IP']


class Philter:
    """ 
        General text filtering class,
        can filter using whitelists, blacklists, regex's and POS
    """

    def __init__(self):
        self.verbose = False
        self.folder = Path(__file__).parent
        self.config_file = self.folder / 'philter_delta.json'
        # print(__file__)

        if not os.path.exists(self.config_file):
            raise Exception("Filepath does not exist", self.config_file)
        self.patterns = json.loads(open(self.config_file, "r").read())
        for obj in self.patterns:
            if 'filepath' in obj:
                obj['filepath'] = str(self.folder / obj['filepath'])

        # All coordinate maps stored here
        self.coordinate_maps = []

        # create a memory for pos tags
        self.pos_tags = {}

        # create a memory for tokenized text
        self.cleaned = {}

        # create a memory for include coordinate map
        self.include_map = CoordinateMap()

        # create a memory for exclude coordinate map
        self.exclude_map = CoordinateMap()

        # create a memory for FULL exclude coordinate map (including non-whitelisted words)
        self.full_exclude_map = {}

        # create a memory for the list of known PHI types
        self.phi_type_list = ['DATE', 'Patient_Social_Security_Number', 'Email', 'Provider_Address_or_Location', 'Age',
                              'Name', 'OTHER', 'ID', 'NAME', 'LOCATION', 'CONTACT', 'AGE', 'URL']

        # create a memory for the corrdinate maps of known PHI types
        self.phi_type_dict = {}
        for phi_type in self.phi_type_list:
            self.phi_type_dict[phi_type] = [CoordinateMap()]

        # create a memory for stored coordinate data
        self.data_all_files = {}

        # create a memory for pattern index, with titles
        self.pattern_indexes = {}

        # initialize our patterns
        self.init_patterns()

    def get_pos(self, id, cleaned):
        if id not in self.pos_tags:
            self.pos_tags = {}
            self.pos_tags[id] = nltk.pos_tag(cleaned)
        return self.pos_tags[id]

    def get_clean(self, id, text, pre_process=r"[^a-zA-Z0-9]"):
        if id not in self.cleaned:
            self.cleaned = {}
            # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list
            lst = re.split(r"(\s+)", text)
            cleaned = []
            for item in lst:
                if len(item) > 0:
                    if not item.isspace():
                        split_item = re.split(r"(\s+)", re.sub(pre_process, " ", item))
                        for elem in split_item:
                            if len(elem) > 0:
                                cleaned.append(elem)
                    else:
                        cleaned.append(item)
            self.cleaned[id] = cleaned
        return self.cleaned[id]

    def init_patterns(self):
        """ given our input pattern config will load our sets and pre-compile our regex"""

        known_pattern_types = {"regex", "set", "regex_context", "stanford_ner", "pos_matcher", "match_all"}
        require_files = {"regex", "set"}
        # require_pos = {"pos_matcher"}
        set_filetypes = {"pkl", "json"}
        regex_filetypes = {"txt"}
        reserved_list = {"data", "coordinate_map"}

        # first check that data is formatted, can be loaded etc.
        for i, pattern in enumerate(self.patterns):
            self.pattern_indexes[pattern['title']] = i
            if pattern["type"] in require_files and not os.path.exists(pattern["filepath"]):
                raise Exception("Config filepath does not exist", pattern["filepath"])
            for k in reserved_list:
                if k in pattern:
                    raise Exception("Error, Keyword is reserved", k, pattern)
            if pattern["type"] not in known_pattern_types:
                raise Exception("Pattern type is unknown", pattern["type"])
            if pattern["type"] == "set":
                if pattern["filepath"].split(".")[-1] not in set_filetypes:
                    raise Exception("Invalid filteype", pattern["filepath"], "must be of", set_filetypes)
                self.patterns[i]["data"] = self.init_set(pattern["filepath"])
            if pattern["type"] == "regex":
                if pattern["filepath"].split(".")[-1] not in regex_filetypes:
                    raise Exception("Invalid filteype", pattern["filepath"], "must be of", regex_filetypes)
                self.patterns[i]["data"] = self.precompile(pattern["filepath"])
            elif pattern["type"] == "regex_context":
                if pattern["filepath"].split(".")[-1] not in regex_filetypes:
                    raise Exception("Invalid filteype", pattern["filepath"], "must be of", regex_filetypes)
                self.patterns[i]["data"] = self.precompile(pattern["filepath"])

    def precompile(self, filepath):
        """ precompiles our regex to speed up pattern matching"""
        regex = open(filepath, "r").read().strip()
        # NOTE: this is not thread safe! but we want to print a more detailed warning message
        with warnings.catch_warnings():
            warnings.simplefilter(action="error", category=FutureWarning)  # in order to print a detailed message
            try:
                re_compiled = re.compile(regex)
            except FutureWarning as warn:
                print("FutureWarning: {0} in file ".format(warn) + filepath)
                warnings.simplefilter(action="ignore", category=FutureWarning)
                re_compiled = re.compile(regex)  # assign nevertheless
                pass
        return re_compiled

    def init_set(self, filepath):
        """ loads a set of words, (must be a dictionary or set shape) returns result"""
        if filepath.endswith(".pkl"):
            try:
                with open(filepath, "rb") as pickle_file:
                    map_set = pickle.load(pickle_file)
            except UnicodeDecodeError:
                with open(filepath, "rb") as pickle_file:
                    map_set = pickle.load(pickle_file, encoding='latin1')
        elif filepath.endswith(".json"):
            map_set = json.loads(open(filepath, "r").read())
        else:
            raise Exception("Invalid filteype", filepath)
        return map_set

    def map_regex(self, id, text, pattern_index=-1, pre_process=r"[^a-zA-Z0-9]"):
        """ Creates a coordinate map from the pattern on this data
            generating a coordinate map of hits given (dry run doesn't transform)
        """
        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(self.patterns))

        coord_map = self.patterns[pattern_index]["coordinate_map"]
        regex = self.patterns[pattern_index]["data"]

        # All regexes except matchall
        if regex != re.compile('.'):
            # if __debug__: print("map_regex(): searching for regex with index " + str(pattern_index))
            # if __debug__ and pattern_index: print("map_regex(): regex is " + str(regex))
            matches = regex.finditer(text)

            for m in matches:
                # print(m.group())
                # print(self.patterns[pattern_index]['title'])

                coord_map.add_extend(id, m.start(), m.start() + len(m.group()))

            self.patterns[pattern_index]["coordinate_map"] = coord_map

        #### MATCHALL/CATCHALL ####
        elif regex == re.compile('.'):
            # Split note the same way we would split for set or POS matching
            matchall_list = re.split(r"(\s+)", text)
            matchall_list_cleaned = []
            for item in matchall_list:
                if len(item) > 0:
                    if item.isspace() == False:
                        split_item = re.split(r"(\s+)", re.sub(pre_process, " ", item))
                        for elem in split_item:
                            if len(elem) > 0:
                                matchall_list_cleaned.append(elem)
                    else:
                        matchall_list_cleaned.append(item)

            start_coordinate = 0
            for word in matchall_list_cleaned:
                start = start_coordinate
                stop = start_coordinate + len(word)
                word_clean = re.sub(r"[^a-zA-Z0-9]+", "", word.lower().strip())
                if len(word_clean) == 0:
                    # got a blank space or something without any characters or digits, move forward
                    start_coordinate += len(word)
                    continue

                if regex.match(word_clean):
                    coord_map.add_extend(id, start, stop)

                # advance our start coordinate
                start_coordinate += len(word)

            self.patterns[pattern_index]["coordinate_map"] = coord_map

    def map_regex_context(self, id="", text="", pattern_index=-1, pre_process=r"[^a-zA-Z0-9]"):
        """ map_regex_context creates a coordinate map from combined regex + PHI coordinates 
        of all previously mapped patterns
        """

        punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")

        # if not os.path.exists(filename):
        #     raise Exception("Filepath does not exist", filename)

        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(self.patterns))

        coord_map = self.patterns[pattern_index]["coordinate_map"]
        regex = self.patterns[pattern_index]["data"]
        context = self.patterns[pattern_index]["context"]
        try:
            context_filter = self.patterns[pattern_index]["context_filter"]
        except KeyError:
            warnings.warn("deprecated missing context_filter field in filter " + str(
                pattern_index) + " of type regex_context, assuming \'all\'", DeprecationWarning)
            context_filter = 'all'

        # Get PHI coordinates
        if context_filter == 'all':
            # current_include_map = self.get_full_include_map(filename)
            current_include_map = self.include_map
            # Create complement exclude map (also excludes punctuation)      
            full_exclude_map = current_include_map.get_complement(id, text)

        else:
            context_filter_pattern_index = self.pattern_indexes[context_filter]
            full_exclude_map_coordinates = self.patterns[context_filter_pattern_index]['coordinate_map']
            full_exclude_map = {}
            for start, stop in full_exclude_map_coordinates.filecoords(id):
                full_exclude_map[start] = stop

        # 1. Get coordinates of all include and exclude mathches

        punctuation_matcher = re.compile(r"[^a-zA-Z0-9*]")
        # 2. Find all patterns expressions that match regular expression
        matches = regex.finditer(text)
        # print(full_exclud_map)
        for m in matches:

            # initialize phi_left and phi_right
            phi_left = False
            phi_right = False

            match_start = m.span()[0]
            match_end = m.span()[1]

            # PHI context left and right
            phi_starts = []
            phi_ends = []
            for start in full_exclude_map:
                phi_starts.append(start)
                phi_ends.append(full_exclude_map[start])

            if match_start in phi_ends:
                phi_left = True

            if match_end in phi_starts:
                phi_right = True

            # Get index of m.group()first alphanumeric character in match
            tokenized_matches = []
            match_text = m.group()
            split_match = re.split(r"(\s+)", re.sub(pre_process, " ", match_text))

            # Get all spans of tokenized match (because remove() function requires tokenized start coordinates)
            coord_tracker = 0
            for element in split_match:
                if element != '':
                    if not punctuation_matcher.match(element[0]):
                        current_start = match_start + coord_tracker
                        current_end = current_start + len(element)
                        tokenized_matches.append((current_start, current_end))

                        coord_tracker += len(element)
                    else:
                        coord_tracker += len(element)

            # Check for context, and add to coordinate map
            if (context == "left" and phi_left == True) or (context == "right" and phi_right == True) or (
                    context == "left_or_right" and (phi_right == True or phi_left == True)) or (
                    context == "left_and_right" and (phi_right == True and phi_left == True)):
                for item in tokenized_matches:
                    coord_map.add_extend(id, item[0], item[1])

        self.patterns[pattern_index]["coordinate_map"] = coord_map

    def map_set(self, id, text, pattern_index=-1):
        """ Creates a coordinate mapping of words any words in this set"""
        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(self.patterns))

        map_set = self.patterns[pattern_index]["data"]
        coord_map = self.patterns[pattern_index]["coordinate_map"]

        # get part of speech we will be sending through this set
        # note, if this is empty we will put all parts of speech through the set
        check_pos = False
        pos_set = set([])
        if "pos" in self.patterns[pattern_index]:
            pos_set = set(self.patterns[pattern_index]["pos"])
        if len(pos_set) > 0:
            check_pos = True

        cleaned = self.get_clean(id, text)
        pos_list = nltk.pos_tag(cleaned)

        start_coordinate = 0
        for tup in pos_list:
            word = tup[0]
            pos = tup[1]
            start = start_coordinate
            stop = start_coordinate + len(word)

            # This converts spaces into empty strings, so we know to skip forward to the next real word
            word_clean = re.sub(r"[^a-zA-Z0-9]+", "", word.lower().strip())
            if len(word_clean) == 0:
                # got a blank space or something without any characters or digits, move forward
                start_coordinate += len(word)
                continue

            if check_pos == False or (check_pos == True and pos in pos_set):
                if word_clean in map_set or word in map_set:
                    coord_map.add_extend(id, start, stop)
                else:
                    pass

            # advance our start coordinate
            start_coordinate += len(word)

        self.patterns[pattern_index]["coordinate_map"] = coord_map

    def map_pos(self, id, text, pattern_index=-1):
        """ Creates a coordinate mapping of words which match this part of speech (POS)"""
        if pattern_index < 0 or pattern_index >= len(self.patterns):
            raise Exception("Invalid pattern index: ", pattern_index, "pattern length", len(self.patterns))

        if "pos" not in self.patterns[pattern_index]:
            raise Exception("Mapping POS must include parts of speech", pattern_index, "pattern length",
                            len(self.patterns))

        coord_map = self.patterns[pattern_index]["coordinate_map"]
        pos_set = set(self.patterns[pattern_index]["pos"])

        # Use pre-process to split sentence by spaces AND symbols, while preserving spaces in the split list

        cleaned = self.get_clean(id, text)

        pos_list = self.get_pos(id, cleaned)  # pos_list = nltk.pos_tag(cleaned)
        # if filename == './data/i2b2_notes/160-03.txt':
        #     print(pos_list)
        start_coordinate = 0
        for tup in pos_list:
            word = tup[0]
            pos = tup[1]
            start = start_coordinate
            stop = start_coordinate + len(word)
            # word_clean = self.get_clean_word2(filename,word)
            word_clean = re.sub(r"[^a-zA-Z0-9]+", "", word.lower().strip())
            if len(word_clean) == 0:
                # got a blank space or something without any characters or digits, move forward
                start_coordinate += len(word)
                continue

            if pos in pos_set:
                coord_map.add_extend(id, start, stop)
                # print("FOUND: ",word,"POS",pos, "COORD: ",  text[start:stop])

            # advance our start coordinate
            start_coordinate += len(word)

        self.patterns[pattern_index]["coordinate_map"] = coord_map

    def get_exclude_include_maps(self, id, pattern, txt):

        coord_map = pattern["coordinate_map"]
        exclude = pattern["exclude"]
        try:
            filter_path = pattern["filepath"]
        except KeyError:
            filter_path = pattern["title"]
        if "phi_type" in pattern:
            phi_type = pattern["phi_type"]
        # self.patterns[pattern_index]["title"]
        else:
            phi_type = "OTHER"

        for start, stop in coord_map.filecoords(id):

            if pattern['type'] != 'regex_context':
                if exclude:
                    if not self.include_map.does_overlap(id, start, stop):
                        self.exclude_map.add_extend(id, start, stop)
                        self.phi_type_dict[phi_type][0].add_extend(id, start, stop)

                else:
                    if not self.exclude_map.does_overlap(id, start, stop):
                        self.include_map.add_extend(id, start, stop)
                        self.data_all_files[id]["non-phi"].append(
                            {"start": start, "stop": stop, "word": txt[start:stop], "filepath": filter_path})

                    else:
                        pass
            ###########################

            # Add regex_context to map separately
            else:
                if exclude:
                    self.exclude_map.add_extend(id, start, stop)
                    self.include_map.remove(id, start, stop)
                    self.phi_type_dict[phi_type][0].add_extend(id, start, stop)
                else:
                    self.include_map.add_extend(id, start, stop)
                    self.exclude_map.remove(id, start, stop)
                    self.data_all_files[id]["non-phi"].append(
                        {"start": start, "stop": stop, "word": txt[start:stop], "filepath": filter_path})

    def deidentify(self, text):
        """
        tagdata['start'], tagdata['stop'], tagdata['word'], tagdata['phi_type']
        :param text:
        :return:
        """

        id = hashlib.md5(text.encode()).hexdigest()

        # create coordinate maps for each pattern
        for i, pat in enumerate(self.patterns):
            self.patterns[i]["coordinate_map"] = CoordinateMap()

        # Get full self.include/exclude map before transform
        self.data_all_files[id] = {"text": text, "phi": [], "non-phi": []}

        # create an intersection map of all coordinates we'll be removing
        self.exclude_map.add_file(id)

        # create an interestion map of all coordinates we'll be keeping
        self.include_map.add_file(id)

        # add file to phi_type_dict
        for phi_type in self.phi_type_list:
            self.phi_type_dict[phi_type][0].add_file(id)

        # Create inital self.exclude/include for file
        for i, pat in enumerate(self.patterns):
            if pat["type"] == "regex":
                self.map_regex(id=id, text=text, pattern_index=i)
            elif pat["type"] == "set":
                self.map_set(id=id, text=text, pattern_index=i)
            elif pat["type"] == "regex_context":
                self.map_regex_context(id=id, text=text, pattern_index=i)
            # elif pat["type"] == "stanford_ner":
            #     self.map_ner(filename=id, text=text, pattern_index=i)
            elif pat["type"] == "pos_matcher":
                self.map_pos(id=id, text=text, pattern_index=i)
            # elif pat["type"] == "match_all":
            #     self.match_all(id=id, text=text, pattern_index=i)
            else:
                raise Exception("Error, pattern type not supported: ", pat["type"])
            self.get_exclude_include_maps(id, pat, text)

        # create intersection maps for all phi types and add them to a dictionary containing all maps

        # get full exclude map (only updated either on-command by map_regex_context or at the very end of map_coordinates)
        self.full_exclude_map[id] = self.include_map.get_complement(id, text)

        for phi_type in self.phi_type_list:
            for start, stop in self.phi_type_dict[phi_type][0].filecoords(id):
                self.data_all_files[id]["phi"].append({
                    "start": start,
                    "stop": stop,
                    "word": text[start:stop],
                    "phi_type": phi_type,
                    "filepath": ""})

        # clear out any data to save ram
        # for i, pat in enumerate(self.patterns):
        #     if "data" in pat:
        #         del self.patterns[i]["data"]

        tagdata = self.data_all_files[id]
        return tagdata['phi']
