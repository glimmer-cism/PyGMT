/* gmtiomodule.c
   Magnus Hagdorn, March 2002

   python module for basic GMT binary grid I/O */

/* PyGMT is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *  
 * PyGMT is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * 
 * You should have received a copy of the GNU General Public License
 * along with PyGMT; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <Python.h>
#include <numpy/arrayobject.h>
#include <gmt.h>
#include <stdio.h>
#include <string.h>
#include <assert.h>

#define PYARRAY(array,i,j) (*(double *) ((array)->data + (i)*(array)->strides[0]+(j)*(array)->strides[1]))

/* prototypes copied from gmt_customio.c */
int GMT_native_read_grd_header (FILE *fp, struct GRD_HEADER *header);
int GMT_native_write_grd_header (FILE *fp, struct GRD_HEADER *header);


void print_header(struct GRD_HEADER header);
static PyObject * gmtio_write(PyObject * self, PyObject * args);
static PyObject * gmtio_read(PyObject * self, PyObject * args);

static PyObject * gmtio_read(PyObject * self, PyObject * args)
{
  PyObject *GMT_file;               /* Python file to write to */
  PyStringObject *GMT_xunits;      /* units in x-direction */
  PyStringObject *GMT_yunits;      /* units in y-direction */
  PyStringObject *GMT_zunits;      /* grid value units */
  PyStringObject *GMT_title;        /* name of data set */
  PyStringObject *GMT_remark;       /* comments re this data set */
  PyArrayObject  *GMT_data;         /* Python array containing data as doubles */
  PyArrayObject  *GMT_xminmax, *GMT_yminmax;

  struct GRD_HEADER gmtheader;    /* GMT header to be written to file */

  FILE *input;                     /* read from this file */
  int dimminmax=2;
  int datadims[2];
  float data;
  int i,j;
  char *filename=NULL;
  int file_type=0; /* can be 1 for a stream or 2 for a file name */

  /* parsing arguments */
  if (!PyArg_ParseTuple(args, "O", &GMT_file))
    return NULL;
      

  /* read GMT header */
  if (PyFile_Check(GMT_file)) /* checking if GMT_file is a file object */
    {
      
      file_type = 1;

      /* getting the file handle */
      input = PyFile_AsFile(GMT_file);

      /* read the header */
      if (GMT_native_read_grd_header(input,&gmtheader)!=GMT_NOERROR)
	{
	  PyErr_SetString(PyExc_IOError, "Error, reading GMT header from file");
	  return NULL;
	}  
    }
  else if (PyString_Check(GMT_file)) /* check if GMT_file is a string (and assume it's a file name) */
    {
      filename = strdup(PyString_AsString(GMT_file)); // DO NOT FREE or modify filename
      assert(filename); 

      file_type = 2;

      /* read the header */
      {
	int argc=1;
	char *argv[]={"gmtiomodule",0};
	const int false=(1==0);
	
	argc=GMT_begin(argc,argv); // Sets crazy globals
	GMT_grd_init (&gmtheader, argc, argv, false); // Initialize grd header structure 
	GMT_read_grd_info (filename,&gmtheader);
      }
    }
  else
    {
      PyErr_SetString(PyExc_TypeError, "Error, need a File object or a file name (string)");
      return NULL;
    }

  /* extracting header information */
  /* creating min/max arrays */
  GMT_xminmax = (PyArrayObject *) PyArray_FromDims(1,&dimminmax,NPY_DOUBLE);
  *(double *) (GMT_xminmax->data) = gmtheader.x_min;
  *(double *) (GMT_xminmax->data+(GMT_xminmax->strides[0])) = gmtheader.x_max;
  GMT_yminmax = (PyArrayObject *) PyArray_FromDims(1,&dimminmax,NPY_DOUBLE);
  *(double *) (GMT_yminmax->data) = gmtheader.y_min;
  *(double *) (GMT_yminmax->data+(GMT_yminmax->strides[0])) = gmtheader.y_max;
  /* strings...*/
  GMT_xunits = (PyStringObject *) PyString_FromString(gmtheader.x_units);
  GMT_yunits = (PyStringObject *) PyString_FromString(gmtheader.y_units);
  GMT_zunits = (PyStringObject *) PyString_FromString(gmtheader.z_units);
  GMT_title = (PyStringObject *) PyString_FromString(gmtheader.title);
  GMT_remark = (PyStringObject *) PyString_FromString(gmtheader.remark);
  
  /* creating data array */
  datadims[0] = gmtheader.nx;
  datadims[1] = gmtheader.ny;
  GMT_data = (PyArrayObject *) PyArray_FromDims(2,datadims,NPY_DOUBLE);

  /* read data */
  if (file_type == 1)
    {
      for (j=gmtheader.ny-1;j>=0;j--)
	for (i=0;i<gmtheader.nx;i++)
	  {
	    fread(&data,sizeof(float),1,input);
	    PYARRAY(GMT_data,i,j) = (double) data;
	  }
    }
  else if (file_type == 2)
    {
      const size_t nm = gmtheader.nx * gmtheader.ny;
      float *a;
      a = (float *) GMT_memory (VNULL, (size_t)nm, sizeof (float), GMT_program);
      
      // Read the entire grd image
      if (GMT_read_grd (filename, &gmtheader, a, 0.0, 0.0, 0.0, 0.0, GMT_pad, FALSE)) {
	// Bad?  free memory and bail
	PyErr_SetString(PyExc_RuntimeError,"Failed to read GMT grid file");
	free(filename);
	return NULL;
      }
      {
	int count=0;
	for (j=gmtheader.ny-1;j>=0;j--)
	  for (i=0;i<gmtheader.nx;i++)
	    {
	      /*data = (float) i + j/10.;*/
	      data = a[count++];
	      PYARRAY(GMT_data,i,j) = (double) data;
	    }
      }
      free (filename);
    }
  else
    {
      PyErr_SetString(PyExc_SystemError,"Shouldn't be here...");
      return NULL;
    }


  return Py_BuildValue("OOiddOOOOOO",
		       GMT_xminmax,
		       GMT_yminmax,
		       gmtheader.node_offset,
		       gmtheader.z_scale_factor,
		       gmtheader. z_add_offset,
		       GMT_xunits,
		       GMT_yunits,
		       GMT_zunits,
		       GMT_title,
		       GMT_remark,
		       GMT_data);

}


static PyObject * gmtio_write(PyObject * self, PyObject * args)
{
  PyObject *GMT_file;               /* Python file to write to */
  PyArrayObject *GMTin_x_minmax;    /* min and max of x coords */
  PyArrayObject *GMTin_y_minmax;    /* min and max of y coords */
  int GMT_node_offset;              /* 0 for node grids, 1 for pixel grids */
  double GMT_z_scale_factor;	  /* grd values must be multiplied by this */
  double GMT_z_add_offset;	  /* After scaling, add this */
  PyStringObject *GMT_xunits;      /* units in x-direction */
  PyStringObject *GMT_yunits;      /* units in y-direction */
  PyStringObject *GMT_zunits;      /* grid value units */
  PyStringObject *GMT_title;        /* name of data set */
  PyStringObject *GMT_remark;       /* comments re this data set */
  PyArrayObject  *GMTin_data;       /* Python array containing grid values */

  PyArrayObject  *GMT_data;         /* Python array containing data as doubles */
  PyArrayObject  *GMT_xminmax, *GMT_yminmax;

  struct GRD_HEADER gmtheader;    /* GMT header to be written to file */

  FILE *output;                     /* write to this file */

  int i,j;
  float data;

  /* parsing arguments */
  if (!PyArg_ParseTuple(args, "O!O!O!iddO!O!O!O!O!O!", 
			&PyFile_Type, &GMT_file, 
			&PyArray_Type, &GMTin_x_minmax,
			&PyArray_Type, &GMTin_y_minmax,
			&GMT_node_offset, &GMT_z_scale_factor, &GMT_z_add_offset,
			&PyString_Type, &GMT_xunits,
			&PyString_Type, &GMT_yunits,
			&PyString_Type, &GMT_zunits,
			&PyString_Type, &GMT_title,
			&PyString_Type, &GMT_remark,
			&PyArray_Type, &GMTin_data))
    return NULL;
  
  /* checking size of (x,y)_minmax */
  if (GMTin_x_minmax->nd != 1 || GMTin_x_minmax->dimensions[0]!=2)
    {
      PyErr_SetString(PyExc_ValueError,"x min max must contain 2 elements");
      return NULL;
    }
  GMT_xminmax = (PyArrayObject *) PyArray_ContiguousFromObject((PyObject *) GMTin_x_minmax, NPY_DOUBLE, 1, 1);
  if (GMTin_y_minmax->nd != 1 || GMTin_y_minmax->dimensions[0]!=2)
    {
      PyErr_SetString(PyExc_ValueError,"y min max must contain 2 elements");
      return NULL;
    }
  GMT_yminmax = (PyArrayObject *) PyArray_ContiguousFromObject((PyObject *) GMTin_y_minmax, NPY_DOUBLE, 1, 1);
  
  /* checking size of input data */
  if (GMTin_data->nd != 2)
    {
      PyErr_SetString(PyExc_ValueError,"input data array must be 2D");
      return NULL;
    } 
  GMT_data = (PyArrayObject *) PyArray_ContiguousFromObject((PyObject *) GMTin_data, NPY_DOUBLE, 2, 2);
  if (GMT_data == NULL)
    return NULL;

  /* filling GMT header */
  gmtheader.nx          = GMT_data->dimensions[0];
  gmtheader.ny          = GMT_data->dimensions[1];
  gmtheader.node_offset = GMT_node_offset;
  gmtheader.x_min       = *(double *) (GMT_xminmax->data);
  gmtheader.x_max       = *(double *) (GMT_xminmax->data + GMT_xminmax->strides[0]);
  gmtheader.y_min       = *(double *) (GMT_yminmax->data);
  gmtheader.y_max       = *(double *) (GMT_yminmax->data + GMT_yminmax->strides[0]);
  /* finding z min/max */
  gmtheader.z_min = *(double *) GMT_data->data;
  gmtheader.z_max = *(double *) GMT_data->data;
  for (i=0;i<GMT_data->dimensions[0];i++)
    for (j=0;j<GMT_data->dimensions[1];j++)
      {
	if (gmtheader.z_min > PYARRAY(GMT_data,i,j))
	  gmtheader.z_min = PYARRAY(GMT_data,i,j);
	if (gmtheader.z_max < PYARRAY(GMT_data,i,j))
	  gmtheader.z_max = PYARRAY(GMT_data,i,j);
      }
  /* setting x_inc, y_inc */
  if (gmtheader.node_offset==0)
    {
      gmtheader.x_inc = (gmtheader.x_max-gmtheader.x_min)/(gmtheader.nx - 1.0);
      gmtheader.y_inc = (gmtheader.y_max-gmtheader.y_min)/(gmtheader.ny - 1.0);
    }
  else if (gmtheader.node_offset==1)
    {
      gmtheader.x_inc = (gmtheader.x_max-gmtheader.x_min)/(gmtheader.nx);
      gmtheader.y_inc = (gmtheader.y_max-gmtheader.y_min)/(gmtheader.ny);
    }
  else
    {
      PyErr_SetString(PyExc_ValueError,"node_offset must be either 0 or 1");
      return NULL;
    }

  /* the rest of the GMT header */
  gmtheader.z_scale_factor = GMT_z_scale_factor;
  gmtheader. z_add_offset  = GMT_z_add_offset;
  strncpy(gmtheader.x_units, PyString_AsString((PyObject *) GMT_xunits), GRD_UNIT_LEN);
  gmtheader.x_units[GRD_UNIT_LEN] = '\0';
  strncpy(gmtheader.y_units, PyString_AsString((PyObject *) GMT_yunits), GRD_UNIT_LEN);
  gmtheader.y_units[GRD_UNIT_LEN] = '\0';
  strncpy(gmtheader.z_units, PyString_AsString((PyObject *) GMT_zunits), GRD_UNIT_LEN);
  gmtheader.z_units[GRD_UNIT_LEN] = '\0';
  strncpy(gmtheader.title, PyString_AsString((PyObject *) GMT_title), GRD_TITLE_LEN);
  gmtheader.title[GRD_TITLE_LEN] = '\0';
  strncpy(gmtheader.command, "produced by Python GMT I/0 module", GRD_COMMAND_LEN); 
  gmtheader.command[GRD_COMMAND_LEN]='\0';
  strncpy(gmtheader.remark, PyString_AsString((PyObject *) GMT_remark), GRD_REMARK_LEN); 
  gmtheader.remark[GRD_REMARK_LEN-1] = '\0'; 
  
  /* checking output */
  output = PyFile_AsFile(GMT_file);
  
  /* writing header to file */
  if (GMT_native_write_grd_header (output, &gmtheader) != GMT_NOERROR)
    {
      PyErr_SetString(PyExc_IOError, "Error, writing GMT header to file");
      return NULL;
    }

  /* writing data */
  for (j=gmtheader.ny-1;j>=0;j--)
    for (i=0;i<gmtheader.nx;i++)
      {
	data = (float) PYARRAY(GMT_data,i,j);
	fwrite(&data, sizeof(float), 1, output);
      }
  
  Py_INCREF(Py_None);
  return Py_None;
}

static PyMethodDef gmtioMethods[] = {
  {"write", gmtio_write, METH_VARARGS, "write GMT binary grids"},
  {"read", gmtio_read, METH_VARARGS, "read GMT binary grids"},
  {NULL, NULL, 0, NULL}        /* Sentinel */
};

void initgmtio(void)
{
  Py_InitModule("gmtio",gmtioMethods);
  import_array();
}







void print_header(struct GRD_HEADER header)
{
  printf("# Title:\t%s\n",header.title);
  printf("# Command:\t%s\n",header.command); 
  printf("# Remark:\t%s\n",header.remark);
  printf("# x-units:\t%s\n",header.x_units);
  printf("# y-units:\t%s\n",header.y_units);
  printf("# z-units:\t%s\n",header.z_units);
  printf("# nx:\t\t%d\n",header.nx);
  printf("# ny:\t\t%d\n",header.ny);
  printf("# x_min:\t%f\n",header.x_min);
  printf("# x_max:\t%f\n",header.x_max);
  printf("# y_min:\t%f\n",header.y_min);
  printf("# y_max:\t%f\n",header.y_max);
  printf("# z_min:\t%f\n",header.z_min);
  printf("# z_max:\t%f\n",header.z_max);
  printf("# x_inc:\t%f\n",header.x_inc);
  printf("# y_inc:\t%f\n",header.y_inc);
  printf("# z_scale_factor:\t%f\n",header.z_scale_factor);
  printf("# z_add_offset:\t%f\n",header.z_add_offset);
  printf("# node_offset:\t%d\n",header.node_offset);  
}
