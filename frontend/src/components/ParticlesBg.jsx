import { useCallback } from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

const ParticlesBg = ({ darkMode }) => {
  const init = useCallback(async (engine) => {
    await loadFull(engine);
  }, []);

  return (
    <Particles
      id="tsparticles"
      init={init}
      options={{
        background: { color: { value: darkMode ? "#0a0a0a" : "#ffffff" } },
        fpsLimit: 60,
        interactivity: {
          events: {
            onHover: { enable: true, mode: "repulse" },
            resize: true,
          },
          modes: { repulse: { distance: 100, duration: 0.4 } },
        },
        particles: {
          color: { value: darkMode ? "#00bfff" : "#4b0082" },
          links: {
            color: darkMode ? "#00bfff" : "#4b0082",
            distance: 150,
            enable: true,
            opacity: 0.3,
            width: 1,
          },
          move: { enable: true, speed: 1, outModes: { default: "bounce" } },
          number: { value: 50, density: { enable: true, area: 800 } },
          opacity: { value: 0.5 },
          shape: { type: "circle" },
          size: { value: { min: 1, max: 4 } },
        },
        detectRetina: true,
      }}
      className="absolute inset-0 -z-10"
    />
  );
};

export default ParticlesBg;
