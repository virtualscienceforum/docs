from pathlib import Path
from datetime import datetime
import re
from string import punctuation

import jinja2
import pytz
from ruamel.yaml import YAML

registration_form_html =
`<!DOCTYPE html>
<head>
<script src='https://www.google.com/recaptcha/api.js'></script>
</head>
<html>
<style>
body {font-family: Arial, Helvetica, sans-serif;}
* {box-sizing: border-box}
/* Full-width input fields */
input[type=text] {
  width: 100%;
  padding: 15px;
  margin: 5px 0 22px 0;
  display: inline-block;
  border: none;
  background: #f1f1f1;
}
input[type=text]:focus {
  background-color: #ddd;
  outline: none;
}
hr {
  border: 1px solid #f1f1f1;
  margin-bottom: 25px;
}
/* Set a style for all buttons */
button {
  background-color: #4CAF50;
  color: white;
  padding: 14px 20px;
  margin: 8px 0;
  border: none;
  cursor: pointer;
  width: 100%;
  opacity: 0.9;
}
button:hover {
  opacity:1;
}
/* Float registration button and add an equal width */
.registerbtn {
  float: left;
  width: 50%;
}
/* Add padding to container elements */
.container {
  padding: 16px;
}
/* Clear floats */
.clearfix::after {
  content: "";
  clear: both;
  display: table;
}
/* Change styles for cancel button and signup button on extra small screens */
@media screen and (max-width: 300px) {
  .cancelbtn, .signupbtn {
     width: 100%;
  }
}
</style>
<body>
<form id="registrationForm" method="post" action="vsf-worker.virtualscienceforum.workers.dev/register" style="border:1px solid #ccc">
  <div class="container">
    <h1>Sign Up</h1>
    <p>Please fill in this form to register for the talk by SPEAKERNAME.</p>
    <hr>
    <label for="firstname"><b>First Name</b></label>
    <input type="text" placeholder="Enter your first name" name="firstname" id="name" required>
    <label for="lastname"><b>Last Name</b></label>
    <input type="text" placeholder="Enter your last name" name="lastname" id="name" required>

    <label for="address"><b>Email</b></label>
    <input type="email" placeholder="Enter your Email" name="address" id="address" required>
    <label for="addressconfirm"><b>Confirm Email</b></label>
    <input type="email" placeholder="Confirm your Email" name="addressconfirm" id="address" required>

    <div id="checkboxes">
        <ul id="checkboxes" style='list-style:none'>
          <li> <input type="checkbox" name="instructions-checkbox" value="confirm-instructions" required> Please confirm you have read the <a href='http://virtualscienceforum.org/#/attendeeguide'>participant instructions*</a> </li>
          <li> <input type="checkbox" name="contact-checkbox" value="confirm-contact" checked> Please check this box if we may contact you about future VSF events </li>
        </ul>
    </div>

    <input type="hidden" name="meetingID" id="meetingID" value="MEETINGID" required>

    <div id="recaptcha" name="recaptcha" class="g-recaptcha" data-sitekey="6Lf37MoZAAAAAF19QdljioXkLIw23w94QWpy9c5E"></div>
    <div class="clearfix">
      <button type="submit" class="registerbtn">Register</button>
    </div>
  </div>
</form>
</body>
</html>`

yaml = YAML(typ='safe')
with open('../talks.yml') as f:
    talks = yaml.load(f)

punctuation_without_dash = punctuation.replace('-','')
translation_table = str.maketrans('','', punctuation_without_dash)
def format_title(s):
    return s.translate(translation_table).replace(' ', '-')

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader('../templates')
)
env.filters['format_title'] = format_title

def update_registration_form(talk):
    talk['registration_form'] = registration_form_html.replace("SPEAKERNAME", talk['speaker_name']).replace("MEETINGID", talk['zoom_meeting_id'])

env.filter['update_registration_form'] = update_registration_form

header = Path("../speakers-corner-header.md").read_text()

for talk in talks:
    talk['time'] = talk['time'].replace(tzinfo=pytz.UTC)
    if re.fullmatch(r"\d{4}\.\d{5}", talk.get("preprint", "")) is None:
        talk.pop("preprint", "")

sc_talks = [talk for talk in talks if talk['event_type'] == 'speakers_corner']
now = datetime.now(tz=pytz.UTC)
upcoming = [talk for talk in sc_talks if talk["time"] > now]
previous = [talk for talk in sc_talks if talk["time"] < now]

Path('../speakers-corner.md').write_text(
    env.get_template('speakers_corner.md.j2').render(
        header=header,
        upcoming=upcoming,
        previous=previous,
    )
)

Path('../long_range_colloquium.md').write_text(
    env.get_template('long_range_colloquium.md.j2').render(
        header=header,
        talks=[talk for talk in talks if talk['event_type'] == 'lrc'],
        now=now
    )
)
