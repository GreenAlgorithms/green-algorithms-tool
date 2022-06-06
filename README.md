# Green Algorithms 
**www.green-algorithms.org**

[![Generic badge](https://img.shields.io/badge/Version-v2.2-blue.svg)](https://shields.io/)
  
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/purple?icon=github)](https://github.com/Naereen/badges/)

---

<img src="assets/images/screenshot_app.png" width="500">


## Methods and data

The methodology behind the Green Algorithms project is described in our publication:
https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707

All the data used for the calculator are in the `/data` directory above. 

## Questions, issues, suggestions? Want to contribute?

Start by opening an issue here, and we will try to address it quickly:
https://github.com/GreenAlgorithms/green-algorithms-tool/issues

You can also contact us at: green.algorithms@gmail.com

## How to cite this work
> Lannelongue, L., Grealey, J., Inouye, M., 
> Green Algorithms: Quantifying the Carbon Footprint of Computation. 
> Adv. Sci. 2021, 2100707. https://doi.org/10.1002/advs.202100707

## FAQ
[![Ask Me Anything !](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)](https://GitHub.com/Naereen/ama)


> Should I include the number of processors, number of cores, or number of threads used?

For CPUs, the number of cores (CPUs usually have 4-12 cores per processor). For GPUs, the number of GPUs. 
If using multi-threading on CPUs (i.e. using more threads than cores), still input the number of cores, 
but be aware that your emissions might be underestimated. 

> What if my processor is not in the list? 

You can select "Other" and find the TDP (Thermal Design Power) value on the manufacturer's website. 
Plus, add a comment on [this issue](https://github.com/GreenAlgorithms/green-algorithms-tool/issues/1) so that we can add it to the list! 

> What if my country is not in the list? 

Add a comment on [this issue](https://github.com/GreenAlgorithms/green-algorithms-tool/issues/2) so that we can add it to the list!  
(some countries are more secretive than others about their energy mix). 
You can use the world average, or a close proxy, for your estimations.

> Can I compare algorithms impact independantly of the location?

Yes, simply use the "Energy needed" (in W) displayed next to the carbon emissions. 

> How do I find the usage factor of my processors?

It depends on your system. For example if you're using SLURM, `seff <job_id>` will give you the "CPU Efficiency". 
Similar commands exist for the different systems, and if you can't find it, you can just leave the default value of 1. 

> How do I estimate my PSF (Pragmatic Scaling Factor)?

Try to estimate how many times you need to run your full analysis to get results you're happy with. 
It can be trials and errors, parameters optimisations, memory issues etc. 

> What if I found a bug in the tool?

[Open an issue](https://github.com/GreenAlgorithms/green-algorithms-tool/issues) on the GitHub so that we can look at it. 

## Credits 

- The app was designed using [Plotly Dash](https://plot.ly/dash/).
- The background image is realised by [Ed Hawkins](https://showyourstripes.info) from the University of Reading.
- The icons used are under [CC Attribution licence](https://creativecommons.org/licenses/by/4.0/) 
and have been designed by 
[Laura Reen](https://icon-icons.com/icon/weather-co2-pollution/90772),
[Jeremiah](https://icon-icons.com/icon/preferences-system-power-energy/103835),
[Sergei Kokota](https://icon-icons.com/icon/tree-greenery-nature/53329),
[Baianat](https://icon-icons.com/icon/car/61086) and
[RoundIcons](https://icon-icons.com/icon/plane-airplane/89770).
- The app has also been improved by [ongcp97](https://www.fiverr.com/ongcp97).

## Licence

This work is licensed under a
[Creative Commons Attribution 4.0 International License][cc-by].

[![CC BY 4.0][cc-by-shield]][cc-by]

[![CC BY 4.0][cc-by-image]][cc-by]

[cc-by]: http://creativecommons.org/licenses/by/4.0/
[cc-by-image]: https://i.creativecommons.org/l/by/4.0/88x31.png
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg

