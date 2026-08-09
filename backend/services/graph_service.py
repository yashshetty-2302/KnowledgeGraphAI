import networkx as nx
import re
from typing import List, Dict, Set, Tuple
import pickle
import os
from config import Config

class GraphService:
    def __init__(self):
        self.graph = nx.DiGraph()
        self.graph_path = os.path.join(Config.DATA_DIR, "knowledge_graph.pkl")
        self._load_or_create_graph()
    
    def _load_or_create_graph(self):
        """Load existing graph or create new one."""
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        if os.path.exists(self.graph_path):
            with open(self.graph_path, 'rb') as f:
                self.graph = pickle.load(f)
        else:
            self.graph = nx.DiGraph()
    
    def extract_entities(self, text: str) -> Set[str]:
        """
        Extract important entities from text.
        Focus on enterprise-relevant terms.
        """
        entities = set()
        
        # Common enterprise patterns
        patterns = [
            # Policies
            r'\b[A-Z][a-z]+\s+(?:policy|Policy|guideline|Guideline|procedure|Procedure)\b',
            # Roles/Positions
            r'\b(?:HR|Human Resources|Director|Manager|Supervisor|Employee|Administrator|Coordinator)\b',
            # Departments
            r'\b(?:HR|IT|Finance|Marketing|Sales|Operations|Engineering|Legal|Security)\s+(?:Department|Dept)\b',
            # Benefits
            r'\b(?:health|dental|vision|life|pet|gym|disability|unemployment)\s+(?:insurance|Insurance|coverage|Coverage)\b',
            r'\b(?:401k|pension|retirement|stock|equity|bonus|vacation|annual|sick|parental|personal)\s+(?:plan|Plan|leave|Leave)\b',
            # Approvals
            r'\b(?:approval|Approval|approval|approve|authorized|authorization)\b',
            # Contracts
            r'\b(?:contract|Contract|agreement|Agreement)\b',
            # Dates/Time
            r'\b(?:90|30|60|180)\s+days?\b',
            r'\b(?:20|10|12|5)\s+(?:days|weeks|years)\b',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Normalize to title case
                entity = ' '.join(word.capitalize() for word in match.split())
                entities.add(entity)
        
        # Extract capitalized words (potential proper nouns/entitites)
        # But filter out common words
        common_words = {'The', 'This', 'That', 'These', 'Those', 'Is', 'Are', 'Was', 'Were', 'Be', 'Been', 'Being', 'Have', 'Has', 'Had', 'Do', 'Does', 'Did', 'Will', 'Would', 'Could', 'Should', 'May', 'Might', 'Must', 'Can', 'Need', 'Want', 'Like', 'Get', 'Got', 'About', 'For', 'With', 'From', 'To', 'In', 'On', 'At', 'By', 'Of', 'As', 'Or', 'And', 'But', 'If', 'Then', 'Than', 'So', 'Very', 'More', 'Most', 'Some', 'Any', 'Such', 'Same', 'Into', 'Over', 'After', 'Before', 'Between', 'Under', 'Again', 'Further', 'Once', 'Here', 'There', 'When', 'Where', 'Why', 'How', 'All', 'Each', 'Few', 'More', 'Most', 'Other', 'Some', 'Such', 'No', 'Nor', 'Not', 'Only', 'Own', 'Same', 'So', 'Than', 'Too', 'Very', 'Chapter', 'Section', 'Page', 'Pdf', 'Document', 'Company', 'Employee', 'Context', 'Information', 'Answer', 'Question', 'Response', 'Available', 'Provided', 'Required', 'According', 'However', 'Therefore', 'Thus', 'Hence', 'Moreover', 'Furthermore', 'Additionally', 'Also', 'Plus', 'Including', 'Included', 'Unless', 'Except', 'Without', 'Within', 'Throughout', 'Through', 'During', 'Before', 'After', 'Since', 'Until', 'While', 'Although', 'Though', 'Because', 'If', 'When', 'Where', 'While', 'Whether', 'Either', 'Neither', 'Both', 'Each', 'Every', 'Any', 'Some', 'All', 'None', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Last', 'Next', 'Previous', 'Following', 'Preceding', 'Such', 'Said', 'States', 'Stated', 'Says', 'Saying', 'Asked', 'Requests', 'Requires', 'Require', 'Allow', 'Allows', 'Allowed', 'Enable', 'Enables', 'Enabled', 'Provide', 'Provides', 'Provided', 'Include', 'Includes', 'Included', 'Contain', 'Contains', 'Contained', 'Exist', 'Exists', 'Existed', 'Available', 'Avail', 'Able', 'Make', 'Makes', 'Made', 'Take', 'Takes', 'Taken', 'Give', 'Gives', 'Given', 'Get', 'Gets', 'Got', 'Come', 'Comes', 'Came', 'Go', 'Goes', 'Went', 'See', 'Sees', 'Saw', 'Know', 'Knows', 'Knew', 'Think', 'Thinks', 'Thought', 'Feel', 'Feels', 'Felt', 'Understand', 'Understands', 'Understood', 'Believe', 'Believes', 'Believed', 'Consider', 'Considers', 'Considered', 'Suppose', 'Supposes', 'Supposed', 'Assume', 'Assumes', 'Assumed', 'Expect', 'Expects', 'Expected', 'Need', 'Needs', 'Needed', 'Want', 'Wants', 'Wanted', 'Hope', 'Hopes', 'Hoped', 'Wish', 'Wishes', 'Wished', 'Desire', 'Desires', 'Desired', 'Plan', 'Plans', 'Planned', 'Decide', 'Decides', 'Decided', 'Choose', 'Chooses', 'Chosen', 'Prefer', 'Prefers', 'Preferred', 'Like', 'Likes', 'Liked', 'Love', 'Loves', 'Loved', 'Hate', 'Hates', 'Hated', 'Start', 'Starts', 'Started', 'Begin', 'Begins', 'Began', 'Beginning', 'End', 'Ends', 'Ended', 'Finish', 'Finishes', 'Finished', 'Complete', 'Completes', 'Completed', 'Continue', 'Continues', 'Continued', 'Stop', 'Stops', 'Stopped', 'Pause', 'Pauses', 'Paused', 'Resume', 'Resumes', 'Resumed', 'Create', 'Creates', 'Created', 'Build', 'Builds', 'Built', 'Make', 'Makes', 'Made', 'Use', 'Uses', 'Used', 'Work', 'Works', 'Worked', 'Play', 'Plays', 'Played', 'Run', 'Runs', 'Ran', 'Walk', 'Walks', 'Walked', 'Talk', 'Talks', 'Talked', 'Speak', 'Speaks', 'Spoke', 'Write', 'Writes', 'Wrote', 'Read', 'Reads', 'Read', 'Listen', 'Listens', 'Listened', 'Watch', 'Watches', 'Watched', 'Look', 'Looks', 'Looked', 'See', 'Sees', 'Saw', 'Hear', 'Hears', 'Heard', 'Smell', 'Smells', 'Smelled', 'Taste', 'Tastes', 'Tasted', 'Touch', 'Touches', 'Touched', 'Feel', 'Feels', 'Felt', 'Think', 'Thinks', 'Thought', 'Believe', 'Believes', 'Believed', 'Know', 'Knows', 'Knew', 'Understand', 'Understands', 'Understood', 'Remember', 'Remembers', 'Remembered', 'Forget', 'Forgets', 'Forgot', 'Learn', 'Learns', 'Learned', 'Teach', 'Teaches', 'Taught', 'Study', 'Studies', 'Studied', 'Practice', 'Practices', 'Practiced', 'Train', 'Trains', 'Trained', 'Help', 'Helps', 'Helped', 'Support', 'Supports', 'Supported', 'Assist', 'Assists', 'Assisted', 'Serve', 'Serves', 'Served', 'Work', 'Works', 'Worked', 'Handle', 'Handles', 'Handled', 'Manage', 'Manages', 'Managed', 'Control', 'Controls', 'Controlled', 'Lead', 'Leads', 'Led', 'Follow', 'Follows', 'Followed', 'Guide', 'Guides', 'Guided', 'Direct', 'Directs', 'Directed', 'Command', 'Commands', 'Commanded', 'Order', 'Orders', 'Ordered', 'Request', 'Requests', 'Requested', 'Ask', 'Asks', 'Asked', 'Answer', 'Answers', 'Answered', 'Reply', 'Replies', 'Replied', 'Respond', 'Responds', 'Responded', 'State', 'States', 'Stated', 'Claim', 'Claims', 'Claimed', 'Suggest', 'Suggests', 'Suggested', 'Propose', 'Proposes', 'Proposed', 'Offer', 'Offers', 'Offered', 'Provide', 'Provides', 'Provided', 'Supply', 'Supplies', 'Supplied', 'Give', 'Gives', 'Given', 'Grant', 'Grants', 'Granted', 'Allow', 'Allows', 'Allowed', 'Permit', 'Permits', 'Permitted', 'Let', 'Lets', 'Let', 'Enable', 'Enables', 'Enabled', 'Cause', 'Causes', 'Caused', 'Result', 'Results', 'Resulted', 'Effect', 'Effects', 'Affected', 'Change', 'Changes', 'Changed', 'Affect', 'Affects', 'Affected', 'Influence', 'Influences', 'Influenced', 'Impact', 'Impacts', 'Impacted', 'Create', 'Creates', 'Created', 'Produce', 'Produces', 'Produced', 'Generate', 'Generates', 'Generated', 'Form', 'Forms', 'Formed', 'Shape', 'Shapes', 'Shaped', 'Build', 'Builds', 'Built', 'Construct', 'Constructs', 'Constructed', 'Establish', 'Establishes', 'Established', 'Found', 'Founds', 'Founded', 'Start', 'Starts', 'Started', 'Begin', 'Begins', 'Began', 'Launch', 'Launches', 'Launched', 'Initiate', 'Initiates', 'Initiated', 'Begin', 'Begins', 'Began', 'Commence', 'Commences', 'Commenced', 'Set', 'Sets', 'Set', 'Put', 'Puts', 'Put', 'Place', 'Places', 'Placed', 'Position', 'Positions', 'Positioned', 'Locate', 'Locates', 'Located', 'Find', 'Finds', 'Found', 'Discover', 'Discovers', 'Discovered', 'Invent', 'Invents', 'Invented', 'Create', 'Creates', 'Created', 'Design', 'Designs', 'Designed', 'Develop', 'Develops', 'Developed', 'Make', 'Makes', 'Made', 'Build', 'Builds', 'Built', 'Write', 'Writes', 'Wrote', 'Compose', 'Composes', 'Composed', 'Paint', 'Paints', 'Painted', 'Draw', 'Draws', 'Drew', 'Sing', 'Sings', 'Sang', 'Dance', 'Dances', 'Danced', 'Act', 'Acts', 'Acted', 'Perform', 'Performs', 'Performed', 'Play', 'Plays', 'Played', 'Run', 'Runs', 'Ran', 'Walk', 'Walks', 'Walked', 'Jump', 'Jumps', 'Jumped', 'Climb', 'Climbs', 'Climbed', 'Swim', 'Swims', 'Swam', 'Fly', 'Flies', 'Flew', 'Drive', 'Drives', 'Drove', 'Ride', 'Rides', 'Rode', 'Travel', 'Travels', 'Traveled', 'Move', 'Moves', 'Moved', 'Go', 'Goes', 'Went', 'Come', 'Comes', 'Came', 'Leave', 'Leaves', 'Left', 'Arrive', 'Arrives', 'Arrived', 'Enter', 'Enters', 'Entered', 'Exit', 'Exits', 'Exited', 'Return', 'Returns', 'Returned', 'Stay', 'Stays', 'Stayed', 'Remain', 'Remains', 'Remained', 'Keep', 'Keeps', 'Kept', 'Hold', 'Holds', 'Held', 'Maintain', 'Maintains', 'Maintained', 'Preserve', 'Preserves', 'Preserved', 'Protect', 'Protects', 'Protected', 'Defend', 'Defends', 'Defended', 'Save', 'Saves', 'Saved', 'Rescue', 'Rescues', 'Rescued', 'Help', 'Helps', 'Helped', 'Serve', 'Serves', 'Served', 'Assist', 'Assists', 'Assisted', 'Support', 'Supports', 'Supported', 'Aid', 'Aids', 'Aided', 'Care', 'Cares', 'Cared', 'Treat', 'Treats', 'Treated', 'Cure', 'Cures', 'Cured', 'Heal', 'Heals', 'Healed', 'Fix', 'Fixes', 'Fixed', 'Repair', 'Repairs', 'Repaired', 'Restore', 'Restores', 'Restored', 'Recover', 'Recovers', 'Recovered', 'Improve', 'Improves', 'Improved', 'Enhance', 'Enhances', 'Enhanced', 'Upgrade', 'Upgrades', 'Upgraded', 'Update', 'Updates', 'Updated', 'Modify', 'Modifies', 'Modified', 'Change', 'Changes', 'Changed', 'Alter', 'Alters', 'Altered', 'Adjust', 'Adjusts', 'Adjusted', 'Adapt', 'Adapts', 'Adapted', 'Adopt', 'Adopts', 'Adopted', 'Accept', 'Accepts', 'Accepted', 'Reject', 'Rejects', 'Rejected', 'Refuse', 'Refuses', 'Refused', 'Deny', 'Denies', 'Denied', 'Allow', 'Allows', 'Allowed', 'Permit', 'Permits', 'Permitted', 'Grant', 'Grants', 'Granted', 'Authorize', 'Authorizes', 'Authorized', 'Approve', 'Approves', 'Approved', 'Endorse', 'Endorses', 'Endorsed', 'Support', 'Supports', 'Supported', 'Back', 'Backs', 'Backed', 'Oppose', 'Opposes', 'Opposed', 'Agree', 'Agrees', 'Agreed', 'Disagree', 'Disagrees', 'Disagreed', 'Consent', 'Consents', 'Consented', 'Object', 'Objects', 'Objected', 'Protest', 'Protests', 'Protested', 'Complain', 'Complains', 'Complained', 'Report', 'Reports', 'Reported', 'Accuse', 'Accuses', 'Accused', 'Blame', 'Blames', 'Blamed', 'Praise', 'Praises', 'Praised', 'Commend', 'Commends', 'Commended', 'Criticize', 'Criticizes', 'Criticized', 'Attack', 'Attacks', 'Attacked', 'Defend', 'Defends', 'Defended', 'Protect', 'Protects', 'Protected', 'Save', 'Saves', 'Saved', 'Rescue', 'Rescues', 'Rescued', 'Help', 'Helps', 'Helped', 'Serve', 'Serves', 'Served', 'Assist', 'Assists', 'Assisted', 'Support', 'Supports', 'Supported', 'Aid', 'Aids', 'Aided', 'Care', 'Cares', 'Cared', 'Treat', 'Treats', 'Treated', 'Cure', 'Cures', 'Cured', 'Heal', 'Heals', 'Healed', 'Fix', 'Fixes', 'Fixed', 'Repair', 'Repairs', 'Repaired', 'Restore', 'Restores', 'Restored', 'Recover', 'Recovers', 'Recovered', 'Improve', 'Improves', 'Improved', 'Enhance', 'Enhances', 'Enhanced', 'Upgrade', 'Upgrades', 'Upgraded', 'Update', 'Updates', 'Updated', 'Modify', 'Modifies', 'Modified', 'Change', 'Changes', 'Changed', 'Alter', 'Alters', 'Altered', 'Adjust', 'Adjusts', 'Adjusted', 'Adapt', 'Adapts', 'Adapted', 'Adopt', 'Adopts', 'Adopted', 'Accept', 'Accepts', 'Accepted', 'Reject', 'Rejects', 'Rejected', 'Refuse', 'Refuses', 'Refused', 'Deny', 'Denies', 'Denied', 'Allow', 'Allows', 'Allowed', 'Permit', 'Permits', 'Permitted', 'Grant', 'Grants', 'Granted', 'Authorize', 'Authorizes', 'Authorized', 'Approve', 'Approves', 'Approved', 'Endorse', 'Endorses', 'Endorsed', 'Support', 'Supports', 'Supported', 'Back', 'Backs', 'Backed', 'Oppose', 'Opposes', 'Opposed', 'Agree', 'Agrees', 'Agreed', 'Disagree', 'Disagrees', 'Disagreed', 'Consent', 'Consents', 'Consented', 'Object', 'Objects', 'Objected', 'Protest', 'Protests', 'Protested', 'Complain', 'Complains', 'Complained', 'Report', 'Reports', 'Reported', 'Accuse', 'Accuses', 'Accused', 'Blame', 'Blames', 'Blamed', 'Praise', 'Praises', 'Praised', 'Commend', 'Commends', 'Commended', 'Criticize', 'Criticizes', 'Criticized', 'Attack', 'Attacks', 'Attacked', 'Defend', 'Defends', 'Defended', 'Protect', 'Protects', 'Protected', 'Save', 'Saves', 'Saved', 'Rescue', 'Rescues', 'Rescued', 'Help', 'Helps', 'Helped', 'Serve', 'Serves', 'Served', 'Assist', 'Assists', 'Assisted', 'Support', 'Supports', 'Supported', 'Aid', 'Aids', 'Aided', 'Care', 'Cares', 'Cared', 'Treat', 'Treats', 'Treated', 'Cure', 'Cures', 'Cured', 'Heal', 'Heals', 'Healed', 'Fix', 'Fixes', 'Fixed', 'Repair', 'Repairs', 'Repaired', 'Restore', 'Restores', 'Restored', 'Recover', 'Recovers', 'Recovered', 'Improve', 'Improves', 'Improved', 'Enhance', 'Enhances', 'Enhanced', 'Upgrade', 'Upgrades', 'Upgraded', 'Update', 'Updates', 'Updated', 'Modify', 'Modifies', 'Modified', 'Change', 'Changes', 'Changed', 'Alter', 'Alters', 'Altered', 'Adjust', 'Adjusts', 'Adjusted', 'Adapt', 'Adapts', 'Adapted', 'Adopt', 'Adopts', 'Adopted', 'Accept', 'Accepts', 'Accepted', 'Reject', 'Rejects', 'Rejected', 'Refuse', 'Refuses', 'Refused', 'Deny', 'Denies', 'Denied', 'Allow', 'Allows', 'Allowed', 'Permit', 'Permits', 'Permitted', 'Grant', 'Grants', 'Granted', 'Authorize', 'Authorizes', 'Authorized', 'Approve', 'Approves', 'Approved', 'Endorse', 'Endorses', 'Endorsed', 'Support', 'Supports', 'Supported', 'Back', 'Backs', 'Backed', 'Oppose', 'Opposes', 'Opposed', 'Agree', 'Agrees', 'Agreed', 'Disagree', 'Disagrees', 'Disagreed', 'Consent', 'Consents', 'Consented', 'Object', 'Objects', 'Objected', 'Protest', 'Protests', 'Protested', 'Complain', 'Complains', 'Complained', 'Report', 'Reports', 'Reported', 'Accuse', 'Accuses', 'Accused', 'Blame', 'Blames', 'Blamed', 'Praise', 'Praises', 'Praised', 'Commend', 'Commends', 'Commended', 'Criticize', 'Criticizes', 'Criticized', 'Attack', 'Attacks', 'Attacked', 'Defend', 'Defends', 'Defended', 'Protect', 'Protects', 'Protected', 'Save', 'Saves', 'Saved', 'Rescue', 'Rescues', 'Rescued', 'Help', 'Helps', 'Helped', 'Serve', 'Serves', 'Served', 'Assist', 'Assists', 'Assisted', 'Support', 'Supports', 'Supported', 'Aid', 'Aids', 'Aided', 'Care', 'Cares', 'Cared', 'Treat', 'Treats', 'Treated', 'Cure', 'Cures', 'Cured', 'Heal', 'Heals', 'Healed', 'Fix', 'Fixes', 'Fixed', 'Repair', 'Repairs', 'Repaired', 'Restore', 'Restores', 'Restored', 'Recover', 'Recovers', 'Recovered', 'Improve', 'Improves', 'Improved', 'Enhance', 'Enhances', 'Enhanced', 'Upgrade', 'Upgrades', 'Upgraded', 'Update', 'Updates', 'Updated', 'Modify', 'Modifies', 'Modified', 'Change', 'Changes', 'Changed', 'Alter', 'Alters', 'Altered', 'Adjust', 'Adjusts', 'Adjusted', 'Adapt', 'Adapts', 'Adapted', 'Adopt', 'Adopts', 'Adopted', 'Accept', 'Accepts', 'Accepted', 'Reject', 'Rejects', 'Rejected', 'Refuse', 'Refuses', 'Refused', 'Deny', 'Denies', 'Denied', 'Allow', 'Allows', 'Allowed', 'Permit', 'Permits', 'Permitted', 'Grant', 'Grants', 'Granted', 'Authorize', 'Authorizes', 'Authorized', 'Approve', 'Approves', 'Approved', 'Endorse', 'Endorses', 'Endorsed', 'Support', 'Supports', 'Supported', 'Back', 'Backs', 'Backed', 'Oppose', 'Opposes', 'Opposed', 'Agree', 'Agrees', 'Agreed', 'Disagree', 'Disagrees', 'Disagreed', 'Consent', 'Consents', 'Consented', 'Object', 'Objects', 'Objected', 'Protest', 'Protests', 'Protested', 'Complain', 'Explain', 'Explains', 'Explained', 'Describe', 'Describes', 'Described', 'Discuss', 'Discusses', 'Discussed', 'Mention', 'Mentions', 'Mentioned', 'State', 'States', 'Stated', 'Declare', 'Declares', 'Declared', 'Announce', 'Announces', 'Announced', 'Proclaim', 'Proclaims', 'Proclaimed', 'Assert', 'Asserts', 'Asserted', 'Claim', 'Claims', 'Claimed', 'Argue', 'Argues', 'Argued', 'Debate', 'Debates', 'Debated', 'Dispute', 'Disputes', 'Disputed', 'Challenge', 'Challenges', 'Challenged', 'Question', 'Questions', 'Questioned', 'Answer', 'Answers', 'Answered', 'Solve', 'Solves', 'Solved', 'Resolve', 'Resolves', 'Resolved', 'Decide', 'Decides', 'Decided', 'Determine', 'Determines', 'Determined', 'Choose', 'Chooses', 'Chosen', 'Select', 'Selects', 'Selected', 'Pick', 'Picks', 'Picked', 'Prefer', 'Prefers', 'Preferred', 'Want', 'Wants', 'Wanted', 'Need', 'Needs', 'Needed', 'Hope', 'Hopes', 'Hoped', 'Wish', 'Wishes', 'Wished', 'Desire', 'Desires', 'Desired', 'Like', 'Likes', 'Liked', 'Love', 'Loves', 'Loved', 'Hate', 'Hates', 'Hated', 'Enjoy', 'Enjoys', 'Enjoyed', 'Prefer', 'Prefers', 'Preferred', 'Value', 'Values', 'Valued', 'Appreciate', 'Appreciates', 'Appreciated', 'Respect', 'Respects', 'Respected', 'Honor', 'Honors', 'Honored', 'Trust', 'Trusts', 'Trusted', 'Believe', 'Believes', 'Believed', 'Confident', 'Confident', 'Confidence', 'Doubt', 'Doubts', 'Doubted', 'Suspect', 'Suspects', 'Suspected', 'Fear', 'Fears', 'Feared', 'Worry', 'Worries', 'Worried', 'Concern', 'Concerns', 'Concerned', 'Anxious', 'Anxieties', 'Anxious', 'Nervous', 'Nervous', 'Relaxed', 'Relaxes', 'Relaxed', 'Calm', 'Calms', 'Calmed', 'Angry', 'Angers', 'Angered', 'Sad', 'Sads', 'Sad', 'Happy', 'Happies', 'Happy', 'Excited', 'Excites', 'Excited', 'Surprised', 'Surprises', 'Surprised', 'Shocked', 'Shocks', 'Shocked', 'Amazed', 'Amazes', 'Amazed', 'Bored', 'Bores', 'Bored', 'Interested', 'Interesteds', 'Interested', 'Curious', 'Curiousness', 'Curious', 'Fascinated', 'Fascinates', 'Fascinated', 'Confused', 'Confuses', 'Confused', 'Puzzled', 'Puzzles', 'Puzzled', 'Satisfied', 'Satisfies', 'Satisfied', 'Disappointed', 'Disappoints', 'Disappointed', 'Proud', 'Prides', 'Proud', 'Ashamed', 'Ashames', 'Ashamed', 'Guilty', 'Guilts', 'Guilty', 'Innocent', 'Innocents', 'Innocent', 'Guilt', 'Guilt', 'Guilt', 'Shame', 'Shame', 'Shame', 'Regret', 'Regrets', 'Regretted', 'Sorry', 'Sorries', 'Sorry', 'Grateful', 'Gratefuls', 'Grateful', 'Thankful', 'Thankful', 'Optimistic', 'Optimistic', 'Optimistic', 'Pessimistic', 'Pessimistic', 'Pessimistic', 'Realistic', 'Realistic', 'Realistic', 'Idealistic', 'Idealistic', 'Idealistic', 'Practical', 'Practical', 'Practical', 'Impatient', 'Impatient', 'Impatient', 'Patient', 'Patients', 'Patient', 'Flexible', 'Flexible', 'Flexible', 'Inflexible', 'Inflexible', 'Inflexible', 'Open', 'Opens', 'Open', 'Closed', 'Closes', 'Closed', 'Honest', 'Honest', 'Honest', 'Dishonest', 'Dishonest', 'Dishonest', 'Reliable', 'Reliable', 'Reliable', 'Unreliable', 'Unreliable', 'Unreliable', 'Dependable', 'Dependable', 'Dependable', 'Independent', 'Independent', 'Independent', 'Responsible', 'Responsible', 'Responsible', 'Irresponsible', 'Irresponsible', 'Capable', 'Capable', 'Capable', 'Incapable', 'Incapable', 'Incapable', 'Available', 'Available', 'Available', 'Unavailable', 'Unavailable', 'Unavailable', 'Possible', 'Possible', 'Possible', 'Impossible', 'Impossible', 'Impossible', 'Probable', 'Probable', 'Probable', 'Improbable', 'Improbable', 'Improbable', 'Certain', 'Certain', 'Certain', 'Uncertain', 'Uncertain', 'Uncertain', 'Likely', 'Likely', 'Likely', 'Unlikely', 'Unlikely', 'Unlikely', 'Ready', 'Ready', 'Ready', 'Unready', 'Unready', 'Unready', 'Willing', 'Willing', 'Willing', 'Unwilling', 'Unwilling', 'Unwilling', 'Able', 'Able', 'Able', 'Unable', 'Unable', 'Unable', 'Free', 'Free', 'Free', 'Busy', 'Busy', 'Busy', 'Occupied', 'Occupied', 'Occupied', 'Available', 'Available', 'Available', 'Engaged', 'Engaged', 'Engaged', 'Unengaged', 'Unengaged', 'Unengaged', 'Focused', 'Focused', 'Focused', 'Distracted', 'Distracted', 'Distracted', 'Concentrated', 'Concentrated', 'Concentrated', 'Scattered', 'Scattered', 'Scattered', 'Organized', 'Organized', 'Organized', 'Disorganized', 'Disorganized', 'Disorganized', 'Messy', 'Messy', 'Messy', 'Neat', 'Neat', 'Neat', 'Clean', 'Clean', 'Clean', 'Dirty', 'Dirty', 'Dirty', 'Efficient', 'Efficient', 'Efficient', 'Inefficient', 'Inefficient', 'Inefficient', 'Effective', 'Effective', 'Effective', 'Ineffective', 'Ineffective', 'Ineffective', 'Successful', 'Successful', 'Successful', 'Unsuccessful', 'Unsuccessful', 'Unsuccessful', 'Productive', 'Productive', 'Productive', 'Unproductive', 'Unproductive', 'Unproductive', 'Creative', 'Creative', 'Creative', 'Uncreative', 'Uncreative', 'Uncreative', 'Innovative', 'Innovative', 'Innovative', 'Traditional', 'Traditional', 'Traditional', 'Modern', 'Modern', 'Modern', 'Outdated', 'Outdated', 'Outdated', 'Current', 'Current', 'Current', 'Obsolete', 'Obsolete', 'Obsolete', 'New', 'New', 'New', 'Old', 'Old', 'Old', 'Young', 'Young', 'Young', 'Fresh', 'Fresh', 'Fresh', 'Stale', 'Stale', 'Stale', 'Recent', 'Recent', 'Recent', 'Ancient', 'Ancient', 'Ancient', 'Modern', 'Modern', 'Modern', 'Futuristic', 'Futuristic', 'Futuristic', 'Primitive', 'Primitive', 'Primitive', 'Advanced', 'Advanced', 'Advanced', 'Basic', 'Basic', 'Basic', 'Simple', 'Simple', 'Simple', 'Complex', 'Complex', 'Complex', 'Complicated', 'Complicated', 'Complicated', 'Easy', 'Easy', 'Easy', 'Difficult', 'Difficult', 'Difficult', 'Hard', 'Hard', 'Hard', 'Soft', 'Soft', 'Soft', 'Rough', 'Rough', 'Rough', 'Smooth', 'Smooth', 'Smooth', 'Sharp', 'Sharp', 'Sharp', 'Dull', 'Dull', 'Dull', 'Bright', 'Bright', 'Bright', 'Dark', 'Dark', 'Dark', 'Light', 'Light', 'Light', 'Heavy', 'Heavy', 'Heavy', 'Lightweight', 'Lightweight', 'Lightweight', 'Heavyweight', 'Heavyweight', 'Heavyweight', 'Big', 'Big', 'Big', 'Small', 'Small', 'Small', 'Huge', 'Huge', 'Huge', 'Tiny', 'Tiny', 'Tiny', 'Long', 'Long', 'Long', 'Short', 'Short', 'Short', 'Tall', 'Tall', 'Tall', 'Short', 'Short', 'Wide', 'Wide', 'Wide', 'Narrow', 'Narrow', 'Narrow', 'Thick', 'Thick', 'Thick', 'Thin', 'Thin', 'Thin', 'Fat', 'Fat', 'Fat', 'Skinny', 'Skinny', 'Skinny', 'Hot', 'Hot', 'Hot', 'Cold', 'Cold', 'Cold', 'Warm', 'Warm', 'Warm', 'Cool', 'Cool', 'Cool', 'Dry', 'Dry', 'Dry', 'Wet', 'Wet', 'Wet', 'Moist', 'Moist', 'Moist', 'Humid', 'Humid', 'Humid', 'Arid', 'Arid', 'Arid', 'Fertile', 'Fertile', 'Fertile', 'Barren', 'Barren', 'Barren', 'Rich', 'Rich', 'Rich', 'Poor', 'Poor', 'Poor', 'Expensive', 'Expen', 'Expen', 'Cheap', 'Cheap', 'Cheap', 'Valuable', 'Valuable', 'Valuable', 'Worthless', 'Worthless', 'Worthless', 'Precious', 'Precious', 'Precious', 'Useful', 'Useful', 'Useful', 'Useless', 'Useless', 'Useless', 'Harmful', 'Harmful', 'Harmful', 'Helpful', 'Helpful', 'Helpful', 'Hurtful', 'Hurtful', 'Hurtful', 'Safe', 'Safe', 'Safe', 'Dangerous', 'Dangerous', 'Dangerous', 'Secure', 'Secure', 'Secure', 'Insecure', 'Insecure', 'Insecure', 'Stable', 'Stable', 'Stable', 'Unstable', 'Unstable', 'Unstable', 'Strong', 'Strong', 'Strong', 'Weak', 'Weak', 'Weak', 'Powerful', 'Powerful', 'Powerful', 'Powerless', 'Powerless', 'Powerless', 'Fast', 'Fast', 'Fast', 'Slow', 'Slow', 'Slow', 'Quick', 'Quick', 'Quick', 'Slow', 'Slow', 'Slow', 'Rapid', 'Rapid', 'Rapid', 'Gradual', 'Gradual', 'Gradual', 'Sudden', 'Sudden', 'Sudden', 'Steady', 'Steady', 'Steady', 'Unsteady', 'Unsteady', 'Unsteady', 'Constant', 'Constant', 'Constant', 'Variable', 'Variable', 'Variable', 'Regular', 'Regular', 'Regular', 'Irregular', 'Irregular', 'Irregular', 'Consistent', 'Consistent', 'Consistent', 'Inconsistent', 'Inconsistent', 'Inconsistent', 'Continuous', 'Continuous', 'Continuous', 'Discontinuous', 'Discontinuous', 'Discontinuous', 'Intermittent', 'Intermittent', 'Intermittent', 'Permanent', 'Permanent', 'Permanent', 'Temporary', 'Temporary', 'Temporary', 'Temporary', 'Brief', 'Brief', 'Brief', 'Long', 'Long', 'Long', 'Short', 'Short', 'Short', 'Instant', 'Instant', 'Instant', 'Gradual', 'Gradual', 'Gradual', 'Sudden', 'Sudden', 'Sudden', 'Steady', 'Steady', 'Steady', 'Unsteady', 'Unsteady', 'Unsteady', 'Constant', 'Constant', 'Constant', 'Variable', 'Variable', 'Variable', 'Regular', 'Regular', 'Regular', 'Irregular', 'Irregular', 'Irregular', 'Consistent', 'Consistent', 'Consistent', 'Inconsistent', 'Inconsistent', 'Inconsistent', 'Continuous', 'Continuous', 'Continuous', 'Discontinuous', 'Discontinuous', 'Discontinuous', 'Intermittent', 'Intermittent', 'Intermittent', 'Permanent', 'Permanent', 'Permanent', 'Temporary', 'Temporary', 'Temporary', 'Temporary', 'Brief', 'Brief', 'Brief', 'Long', 'Long', 'Long', 'Short', 'Short', 'Short', 'Instant', 'Instant', 'Instant', 'Gradual', 'Gradual', 'Gradual', 'Sudden', 'Sudden', 'Sudden', 'Steady', 'Steady', 'Steady', 'Unsteady', 'Unsteady', 'Unsteady', 'Constant', 'Constant', 'Constant', 'Variable', 'Variable', 'Variable', 'Regular', 'Regular', 'Regular', 'Irregular', 'Irregular', 'Irregular', 'Consistent', 'Consistent', 'Consistent', 'Inconsistent', 'Inconsistent', 'Inconsistent', 'Continuous', 'Continuous', 'Continuous', 'Discontinuous', 'Discontinuous', 'Discontinuous', 'Intermittent', 'Intermittent', 'Intermittent', 'Permanent', 'Permanent', 'Permanent', 'Temporary', 'Temporary', 'Temporary', 'Temporary', 'Brief', 'Brief', 'Brief', 'Long', 'Long', 'Long', 'Short', 'Short', 'Short', 'Instant', 'Instant', 'Instant', 'Gradual', 'Gradual', 'Gradual', 'Sudden', 'Sudden', 'Sudden', 'Steady', 'Steady', 'Steady', 'Unsteady', 'Unsteady', 'Unsteady', 'Constant', 'Constant', 'Constant', 'Variable', 'Variable', 'Variable', 'Regular', 'Regular', 'Regular', 'Irregular', 'Irregular', 'Irregular', 'Consistent', 'Consistent', 'Consistent', 'Inconsistent', 'Inconsistent', 'Inconsistent', 'Continuous', 'Continuous', 'Continuous', 'Discontinuous', 'Discontinuous', 'Discontinuous', 'Intermittent', 'Intermittent', 'Intermittent', 'Permanent', 'Permanent', 'Permanent', 'Temporary', 'Temporary', 'Temporary', 'Temporary', 'Brief', 'Brief', 'Brief', 'Long', 'Long', 'Long', 'Short', 'Short', 'Short', 'Instant', 'Instant', 'Instant', 'Gradual', 'Gradual', 'Gradual', 'Sudden', 'Sudden', 'Sudden', 'Steady', 'Steady', 'Steady', 'Unsteady', 'Unsteady', 'Unsteady', 'Constant', 'Constant', 'Constant', 'Variable', 'Variable', 'Variable', 'Regular', 'Regular', 'Regular', 'Irregular', 'Irregular', 'Irregular', 'Consistent', 'Consistent', 'Consistent', 'Inconsistent', 'Inconsistent', 'Inconsistent', 'Continuous', 'Continuous', 'Continuous', 'Discontinuous', 'Discontinuous', 'Discontinuous', 'Intermittent', 'Intermittent, Intermit'}
        
        # Extract capitalized multi-word terms (2-3 words)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}\b', text)
        for term in capitalized_terms:
            if term not in common_words:
                entities.add(term)
        
        return entities
    
    def extract_relationships(self, text: str, entities: Set[str]) -> List[Tuple[str, str, str]]:
        """
        Extract relationships between entities from text.
        Returns list of (source, target, relationship) tuples.
        """
        relationships = []
        entity_list = list(entities)
        text_lower = text.lower()
        
        # Very simple keyword-based relationship extraction
        # Look for patterns like "Entity A requires Entity B"
        keywords = {
            'requires': 'requires',
            'needs': 'requires',
            'approved by': 'approved_by',
            'authorized by': 'approved_by',
            'affects': 'affects',
            'impacts': 'affects',
            'provides': 'provides',
            'managed by': 'managed_by'
        }
        
        for entity in entity_list:
            entity_lower = entity.lower()
            if entity_lower not in text_lower:
                continue
                
            for target in entity_list:
                if target == entity:
                    continue
                target_lower = target.lower()
                if target_lower not in text_lower:
                    continue
                
                # Check each keyword
                for keyword, relation_type in keywords.items():
                    if keyword in text_lower:
                        # Very basic positional check
                        entity_pos = text_lower.find(entity_lower)
                        target_pos = text_lower.find(target_lower)
                        keyword_pos = text_lower.find(keyword)
                        
                        # If keyword is between the two entities
                        if min(entity_pos, target_pos) < keyword_pos < max(entity_pos, target_pos):
                            if entity_pos < target_pos:
                                relationships.append((entity, target, relation_type))
                            else:
                                relationships.append((target, entity, relation_type))
                            break  # One relationship per pair is enough
        
        return relationships
    
    def add_document_to_graph(self, chunks: List[Dict], document_name: str):
        """Extract entities and relationships from document chunks and add to graph."""
        for chunk in chunks:
            text = chunk['text']
            chunk_id = chunk['chunk_id']
            
            try:
                # Extract entities
                entities = self.extract_entities(text)
                
                # Add entities as nodes with metadata
                for entity in entities:
                    if not self.graph.has_node(entity):
                        self.graph.add_node(entity, type='entity')
                    
                    # Add document reference
                    if 'documents' not in self.graph.nodes[entity]:
                        self.graph.nodes[entity]['documents'] = []
                    self.graph.nodes[entity]['documents'].append({
                        'document': document_name,
                        'chunk_id': chunk_id,
                        'page': chunk['page']
                    })
                
                # Extract relationships
                relationships = self.extract_relationships(text, entities)
                
                # Add relationships as edges
                for source, target, relation_type in relationships:
                    if not self.graph.has_edge(source, target):
                        self.graph.add_edge(source, target, relation_type=relation_type, 
                                        documents=[{
                                            'document': document_name,
                                            'chunk_id': chunk_id,
                                            'page': chunk['page']
                                        }])
                    else:
                        # Add document reference to existing edge
                        edge_data = self.graph[source][target]
                        if 'documents' not in edge_data:
                            edge_data['documents'] = []
                        edge_data['documents'].append({
                            'document': document_name,
                            'chunk_id': chunk_id,
                            'page': chunk['page']
                        })
            except Exception as e:
                print(f"Error processing chunk {chunk_id}: {e}")
                continue
        
        self._save_graph()
    
    def search_graph(self, question: str) -> Tuple[List[str], List[Tuple[str, str, str]]]:
        """
        Search graph for entities and relationships relevant to the question.
        
        Returns:
            Tuple of (entities, relationships)
        """
        # Extract entities from question
        question_entities = self.extract_entities(question)
        
        # Find matching entities in graph (more lenient matching)
        matched_entities = []
        for entity in question_entities:
            for graph_entity in self.graph.nodes():
                # Check for partial match (at least 3 characters overlap)
                entity_lower = entity.lower()
                graph_entity_lower = graph_entity.lower()
                if entity_lower in graph_entity_lower or graph_entity_lower in entity_lower:
                    matched_entities.append(graph_entity)
                elif len(entity_lower) >= 3 and entity_lower[:3] in graph_entity_lower:
                    matched_entities.append(graph_entity)
        
        # If no matches, return all graph entities (fallback)
        if not matched_entities and self.graph.number_of_nodes() > 0:
            matched_entities = list(self.graph.nodes())[:5]  # Limit to top 5
        
        # Find relationships for matched entities
        matched_relationships = []
        for entity in matched_entities:
            # Get outgoing relationships
            if self.graph.has_node(entity):
                for target in self.graph.successors(entity):
                    edge_data = self.graph[entity][target]
                    # Edge data is a dict of attributes
                    if isinstance(edge_data, dict):
                        relation_type = edge_data.get('relation', 'related_to')
                        matched_relationships.append((entity, target, relation_type))
                    else:
                        # Fallback for unexpected structure
                        matched_relationships.append((entity, target, 'related_to'))
        
        return matched_entities, matched_relationships
    
    def get_relevant_chunks_from_graph(self, entities: List[str], relationships: List[Tuple[str, str, str]]) -> List[Dict]:
        """Get chunk information for graph entities and relationships."""
        relevant_chunks = set()
        
        for entity in entities:
            if self.graph.has_node(entity):
                for doc_ref in self.graph.nodes[entity].get('documents', []):
                    relevant_chunks.add(doc_ref['chunk_id'])
        
        for source, target, relation in relationships:
            if self.graph.has_edge(source, target):
                for edge_data in self.graph[source][target].values():
                    if isinstance(edge_data, dict) and 'documents' in edge_data:
                        for doc_ref in edge_data['documents']:
                            relevant_chunks.add(doc_ref['chunk_id'])
        
        return list(relevant_chunks)
    
    def _save_graph(self):
        """Save graph to disk."""
        with open(self.graph_path, 'wb') as f:
            pickle.dump(self.graph, f)
    
    def clear(self):
        """Clear the graph."""
        self.graph = nx.DiGraph()
        self._save_graph()
    
    def get_graph_info(self) -> Dict:
        """Get graph statistics."""
        return {
            "nodes": self.graph.number_of_nodes(),
            "edges": self.graph.number_of_edges(),
            "entities": list(self.graph.nodes()),
            "relationships": list(self.graph.edges(data=True))
        }