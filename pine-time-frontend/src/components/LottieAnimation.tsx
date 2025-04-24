import React, { forwardRef, useEffect, useImperativeHandle, useRef } from 'react';
import lottie, { AnimationItem } from 'lottie-web';

interface LottieAnimationProps {
  animationData: any;
  loop?: boolean;
  autoplay?: boolean;
  style?: React.CSSProperties;
  className?: string;
  onComplete?: () => void;
}

const LottieAnimation = forwardRef<any, LottieAnimationProps>(
  ({ animationData, loop = true, autoplay = true, style, className, onComplete }, ref) => {
    const animationContainer = useRef<HTMLDivElement>(null);
    const animationInstance = useRef<AnimationItem | null>(null);

    useImperativeHandle(ref, () => ({
      play: () => {
        if (animationInstance.current) {
          animationInstance.current.play();
        }
      },
      pause: () => {
        if (animationInstance.current) {
          animationInstance.current.pause();
        }
      },
      stop: () => {
        if (animationInstance.current) {
          animationInstance.current.stop();
        }
      },
      goToAndPlay: (frame: number) => {
        if (animationInstance.current) {
          animationInstance.current.goToAndPlay(frame, true);
        }
      },
      goToAndStop: (frame: number) => {
        if (animationInstance.current) {
          animationInstance.current.goToAndStop(frame, true);
        }
      }
    }));

    useEffect(() => {
      if (animationContainer.current) {
        animationInstance.current = lottie.loadAnimation({
          container: animationContainer.current,
          renderer: 'svg',
          loop,
          autoplay,
          animationData,
        });

        if (onComplete) {
          animationInstance.current.addEventListener('complete', onComplete);
        }
      }

      return () => {
        if (animationInstance.current) {
          if (onComplete) {
            animationInstance.current.removeEventListener('complete', onComplete);
          }
          animationInstance.current.destroy();
          animationInstance.current = null;
        }
      };
    }, [animationData, loop, autoplay, onComplete]);

    return <div ref={animationContainer} style={style} className={className} />;
  }
);

LottieAnimation.displayName = 'LottieAnimation';

export default LottieAnimation;
