import fmake


@fmake.program
def example(test = "hello"):
    print(test)

    


@fmake.program
def example1(t1, t2 = "world"):
    return t1 + " " + t2


@fmake.program
def example2():
    print("Example 2", fmake.mdenv["last_return"] )
    return fmake.mdenv["last_return"] 


@fmake.program
def draw_picture():
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Create a simple plot
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(8, 6))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.xlabel('X axis')
    plt.ylabel('Y axis')
    plt.title('Simple Sine Wave')
    plt.grid(True)
    
    # Save the plot
    plt.savefig(fmake.mdenv["last_return"] , dpi=100, bbox_inches='tight')
    plt.close()
    
    return fmake.mdenv["last_return"] 
