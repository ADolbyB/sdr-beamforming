# GNURadio References:

In this subfolder, we have Flow Graph examples we used and made for this Project, along with any other useful resources noted in this README file.

<div align="center">

<img src="./assets/GNUradio.png" alt="Pluto SDR Before Mod" width="600"/><br>
<a href="https://donorbox.org/gnuradio"><small>Image Source. (Donate to GNU radio here)</small></a>

</div>

---

- [GNU Radio](https://wiki.gnuradio.org/index.php/InstallingGR) 
- [GNU Radio Tutorials](https://wiki.gnuradio.org/index.php?title=Tutorials)

When running a GNURadio Flow Graph which requires realtime scheduling, if the following error message in the
console is encountered:

```python
def main(top_block_cls=transceiver_CSS_loopback, options=None):   
    if gr.enable_realtime_scheduling() != gr.RT_OK:   
        gr.logger("realtime").warning("Error: failed to enable real-time scheduling.")
AttributeError: 'gnuradio.gr.gr_python.logger' object has no attribute 'warning'
```

The fix is to allow user's tasks gain the ability to ask for real-time scheduling. Run the following in a terminal:

```bash
echo "$(whoami)  -  rtprio  99" | sudo tee /etc/security/limits.d/99-rtprio.conf
```

Then perform a reboot and the problem should be solved. Thanks to [This GitHub Issue #6923](https://github.com/gnuradio/gnuradio/issues/6923) for the solution.