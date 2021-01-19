/*==============================================================================

  Copyright (c) Kitware, Inc.

  See http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Julien Finet, Kitware, Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

#ifndef __qSlicerQReadsAppMainWindow_h
#define __qSlicerQReadsAppMainWindow_h

// SlicerQReads includes
#include "qSlicerQReadsAppExport.h"
class qSlicerQReadsAppMainWindowPrivate;

// Slicer includes
#include "qSlicerMainWindow.h"

class Q_SLICERQREADS_APP_EXPORT qSlicerQReadsAppMainWindow : public qSlicerMainWindow
{
  Q_OBJECT
public:
  typedef qSlicerMainWindow Superclass;

  qSlicerQReadsAppMainWindow(QWidget *parent=0);
  virtual ~qSlicerQReadsAppMainWindow();

public slots:
  void on_HelpAboutSlicerQReadsAppAction_triggered();

protected:
  qSlicerQReadsAppMainWindow(qSlicerQReadsAppMainWindowPrivate* pimpl, QWidget* parent);

private:
  Q_DECLARE_PRIVATE(qSlicerQReadsAppMainWindow);
  Q_DISABLE_COPY(qSlicerQReadsAppMainWindow);
};

#endif
