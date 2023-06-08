!INC Local Scripts.EAConstants-JScript
!INC User Scripts.Library
!INC EAScriptLib.JScript-Dialog

var tipe as EA.Stereotype;
var tipes = "";
for (var t=0; t<Repository.Stereotypes.Count; t++) {
	tipe = Repository.Stereotypes.GetAt(t);
	if (tipe.Name.indexOf('STEP ') == 0) {
		tipes += tipe.Name.substring(4,100) + ',';
	}
}

var answer = DLGInputBox(tipes, "Set Stereotype", "UserType");
if (answer) {
	Session.Output(answer);
	set_stereotype('STEP '+answer);
}
