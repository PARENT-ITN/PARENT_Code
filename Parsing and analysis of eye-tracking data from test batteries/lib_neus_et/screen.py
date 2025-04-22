"""
Screen class that deals with screen size.
"""
from numpy import sqrt, tan, arctan, pi, nan,  array, abs, logical_or
import warnings

# TODO: use decorators to check for input shapes instead of what is done now

class Screen():

    """
    This class is used to convert easily different types of coordinates for gaze position into each other. There are three types of coordinates:

    - position: values for each coordinate are numbers between 0 and 1. Origin is in the top left corner.
    - pixel: values in screen pixels. Origin is in the top left corner.
    - angle: values for each coordinate are in visual angles. Origin is the centre of the screen.
    """

    def __init__(self, params):


        self.diagonal = params['diagonal']  # in cm (diagonal)
        self.resolution = {'W' : params['resolution']['width'], 'H' : params['resolution']['height']} # in pixels
        self.size = {'W' : params['size']['width'] / 10.0, 'H' : params['size']['height'] / 10.0} # in cm

        self.distance = params['distance'] # in cm

        if not self.check_size():
            warnings.warn('The diagonal size given is not compatible with the sizes of the screen.')
        

        # Save the size of the screen in visual angles

        self.angle = {'W' : 360 * arctan(self.size['W'] / (2 * self.distance)) / pi, 'H' : 360 * arctan(self.size['H'] / (2 * self.distance)) / pi} # in degrees



    def convert(self, x, input, output, direction='both', degrees=True) -> array:

        """
        Function to transform any coordinate to any other.

        :param x: Array containing the gaze positions to convert.
        :type x: numpy.ndarray
        :param input: Type of coordinates used in array x.
        :type input: "position", "pixel" or "angle"
        :param output: Type of coordinates used in return array.
        :type output: "position", "pixel" or "angle"
        :param degrees: If True any angle value is intended to be given in degrees, otherwise radians are used.
        :type degrees: bool

        :return: Array of converted values.
        """

        if input not in ['position', 'pixel', 'angle']:
            raise ValueError(f'Error: input parameter must come from ["position", "pixel", "angle"]. Got "{input}" instead.')
        
        if output not in ['position', 'pixel', 'angle']:
            raise ValueError(f'Error: output parameter must come from ["position", "pixel", "angle"]. Got "{output}" instead.')


        if input == output:
            return x
        
        fun = {'pixel' : {'position' : lambda x: self.pixel_to_pos(x, direction=direction),
                          'angle' : lambda x: self.pixel_to_angle(x, degrees=degrees, direction=direction)},
                'position' : {'pixel' : lambda x: self.pos_to_pixel(x, direction=direction),
                          'angle' : lambda x: self.pos_to_angle(x, degrees=degrees, direction=direction)},
                'angle' : {'pixel' : lambda x: self.angle_to_pixel(x, degrees=degrees, direction=direction),
                          'position' : lambda x: self.angle_to_pos(x, degrees=degrees, direction=direction)}}

        return fun[input][output](x)


    def pos_to_angle(self, x, direction='both', degrees = True):

        """
        Returns the value of coordinates in visual angles. The origin is in the center of the screen.
        """

        self._check_shape(x, direction=direction)

        if degrees:
            coef = 180/pi
        else:
            coef = 1.0

        if direction == 'x':

            size = array([self.size['W']]) # remember that the y-axis is reversed in pos coordinates.

        elif direction == 'y':

            size = array([-self.size['H']]) # remember that the y-axis is reversed in pos coordinates.
        
        else:

            size = array([self.size['W'], -self.size['H']]) # remember that the y-axis is reversed in pos coordinates. 

        x = size * (x - .5)

        return coef * arctan(x/self.distance)
    
    def angle_to_pos(self, x, direction='both', degrees=True):

        """
        Returns the values of coordinates as percentage of the screen (between 0 and 1). The origin is the top left corner.
        """

        self._check_shape(x, direction=direction)

        if degrees:
            coef = pi/180
        else:
            coef = 1.0

        if direction == 'x':

            size = array([self.size['W']]) # remember that the y-axis is reversed in pos coordinates.

        elif direction == 'y':

            size = array([-self.size['H']]) # remember that the y-axis is reversed in pos coordinates.
        
        else:

            size = array([self.size['W'], -self.size['H']]) # remember that the y-axis is reversed in pos coordinates. 

        pos = self.distance * tan(coef * x) / size

        # Check if outside of the screen 

        if direction == 'both':

            ind = logical_or.reduce(abs(pos) > .5, axis=1).astype('bool')

        else:

            ind = (abs(pos) > .5).astype('bool')

        pos[ind] = nan


        return pos + .5
    

    def pixel_to_pos(self, x, direction='both'):

        """
        Returns the values of coordinates as percentage of the screen (between 0 and 1) from pixels. The origin is the top left corner.
        """
        self._check_shape(x, direction=direction)

        
        if direction == 'x':

           resolution = array([self.resolution['W']]) # remember that the y-axis is reversed in pos coordinates.

        elif direction == 'y':

            resolution = array([self.resolution['H']]) # remember that the y-axis is reversed in pos coordinates.
        
        else:

            resolution = array([self.resolution['W'], self.resolution['H']]) # remember that the y-axis is reversed in pos coordinates.

        return x / resolution
    
    def pos_to_pixel(self, x, direction='both'):

        """
        Returns the values of coordinates pixels from percentage of the screen (between 0 and 1). The origin is the top left corner.
        """

        self._check_shape(x, direction=direction)

        
        if direction == 'x':

           resolution = array([self.resolution['W']]) # remember that the y-axis is reversed in pos coordinates.

        elif direction == 'y':

            resolution = array([self.resolution['H']]) # remember that the y-axis is reversed in pos coordinates.
        
        else:

            resolution = array([self.resolution['W'], self.resolution['H']]) # remember that the y-axis is reversed in pos coordinates.

        return x * resolution
    

    def pixel_to_angle(self, x, direction='both', degrees=True):

        """
        Returns the value of coordinates in visual angles. The origin is in the center of the screen.
        """

        return self.pos_to_angle(self.pixel_to_pos(x, direction=direction), direction=direction, degrees=degrees)
    
    def angle_to_pixel(self, x, direction='both', degrees=True):

        """
        Returns the value of coordinates in pixels from visual angles. The origin is top left corner.
        """

        return self.pos_to_pixel(self.angle_to_pos(x, direction=direction, degrees=degrees), direction=direction)
    
  


    def check_size(self, error = 0.05):

        """
        Checks if the size of the diagonal is the same as the one obtained from the vertical and horizontal sizes. Default 5% error is allowed.
        """

        correct_size = sqrt(self.size['W'] ** 2 + self.size['H'] ** 2)

        return abs((correct_size - self.diagonal) / correct_size) <= error
    


    def _check_shape(self, x, direction='both'):

        if direction not in ['x', 'y', 'both']:

            raise ValueError(f'The direction must come from ["x", "y", "both"]. Got {direction} instead.')
        
        if direction == 'both' and (len(x.shape) < 2 or x.shape[1] != 2):
            raise ValueError('If direction is both the array must contain two dimensions.')
        
        if direction != 'both' and (len(x.shape) != 1):
            raise ValueError(f'If direction is {direction} the array must contain one dimension.')
