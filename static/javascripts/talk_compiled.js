$(document).ready(function(){$("textarea:visible:enabled:first").focus();$("input[type=text]:visible:enabled:first").focus();$("#id_body").keypress(function(B){if(B.which==13){return false}var A=(B.which==32||B.which==9||(65<=B.which&&B.which<=65+25)||(97<=B.which&&B.which<=97+25));if((this.value.length>=140)&&(A)){return false}else{return true}});$("#id_body").keyup(function(A){$("#character_count").text(this.value.length);return true});$("#id_body").change(function(A){this.value=this.value.substring(0,140);$("#character_count").text(this.value.length)});$("#id_body").blur(function(A){this.value=this.value.substring(0,140);$("#character_count").text(this.value.length)});$("a.destroy").click(function(A){return confirm("Are you sure?")});$("#posts form").submit(function(B){var A=$("#id_body");var C=A.val();if(C&&C!=""){A.hide();return true}else{return false}});if($(".auto_reload #post_list").size()==1){setInterval(function(A){$("#post_list").load("/?output=ajax")},30000)}});