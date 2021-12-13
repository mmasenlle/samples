header='''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
    <title>Equations</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="static/bootstrap.min.css">
    <link href="static/font-awesome.min.css" rel="stylesheet">
    <script src="static/jquery.min.js"></script>
    <script src="static/popper.min.js"></script>
    <script src="static/bootstrap.min.js"></script>
    <script src="static/plotly-latest.min.js"></script>
    <script src="static/jquery.cookie.min.js"></script>
<script type="text/javascript" src="static/LaTeXMathML.js"></script>
</head>
<body>
'''

footer='</body></html>'

equations=(
'$y=\sqrt{1-x^2}$',
r'''\begin{equation}T\left(\mathbf{r}, t\right) = \frac{\alpha}{K} \int_0^t d\tau \int_R \mathcal{G}\left(\mathbf{r}, t | \mathbf{r}', \tau \right) \delta\left(\mathbf{r}'\right) Q\left(\tau\right) dv.\end{equation}''',

)

def print_equation(eq):
    print('<pre class="LaTeX"><div>',eq,'</div></pre>')
    print('<button class="btn" onclick="navigator.clipboard.writeText(\'',eq.replace('\\','\\\\').replace('\'','\\\''),'\')"><i class="fa fa-copy"></i></button>')


print(header)
for eq in equations:
    print_equation(eq)
print(footer)





