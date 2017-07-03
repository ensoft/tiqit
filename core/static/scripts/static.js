//
// Note Templates
//

var noteTemplates = new Object();
noteTemplates['Release-note'] = "<!--                    RELEASE NOTE TEMPLATE-->\n\
<!-- All text within the markers on these lines are comments intended-->\n\
<!-- to help you fill out this release note.  Anything within these-->\n\
<!-- markers will not appear in the release note.  Do not put any-->\n\
<!-- release note text within these markers.  Any text found between-->\n\
<!-- these markers is safe to be deleted.-->\n\
\n\
<B>Symptom:</B>\n\
\n\
<!-- The symptom is a clear, brief description of the problem symptoms-->\n\
<!-- that help the customers match the bug to something they see in-->\n\
<!-- their device.  Any commands should be in bold print, and any-->\n\
<!-- command argument placeholders should be italicized by using the-->\n\
<!-- <CmdBold>, <noCmdBold>, <CmdArg>, and <noCmdArg> directives-->\n\
\n\
<B>Conditions:</B>\n\
\n\
<!-- Describe the customer environment and any commands that-->\n\
<!-- create the problem (if relevant). If the bug only affects-->\n\
<!-- certain software releases, state which ones.-->\n\
\n\
<B>Workaround:</B>\n\
\n\
<!-- This section describes any workarounds available and any-->\n\
<!-- limitations the workaround may place on the customer.-->\n\
\n\
<B>Further Problem Description:</B>\n\
\n\
<!-- This section can include additional information to allow the-->\n\
<!-- customer to understand the problem in more detail.-->\n\
<!---->\n\
<!-- This field might include:-->\n\
<!--   A broader description of the conditions under which the problem-->\n\
<!--   might occur.  Description of why the problem occurred (e.g.,-->\n\
<!--   RFC noncompliance).-->\n\
<!---->\n\
<!-- Don't include customer configurations, customer names, passwords,-->\n\
<!-- decoded stack traces, or any other information that could-->\n\
<!-- compromise a site's security.-->\n\
";
