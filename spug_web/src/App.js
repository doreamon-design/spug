/**
 * Copyright (c) OpenSpug Organization. https://github.com/openspug/spug
 * Copyright (c) <spug.dev@gmail.com>
 * Released under the AGPL-3.0 License.
 */
import React, { Component } from 'react';
import {Switch, Route} from 'react-router-dom';
import { history, updatePermissions } from 'libs';
import { Result, Spin } from 'antd';
import doreamon from '@zodash/doreamon';
import Login from './pages/login';
import WebSSH from './pages/ssh';
import Layout from './layout';

class App extends Component {
  state = {
    isLoginChecking: true,
    isPermissionDenied: false,
    isBanned: false,
  };

  componentDidMount() {
    setTimeout(async () => {
      try {
        const response = await doreamon.request.get('/api/account/token/', {
          headers: {
            'X-Token': localStorage.getItem('token'),
          },
        }).json();

        const data = response.data;

        // console.log('data:', data);
        if (data.is_active === false || data.is_banned === true) {
          this.setState({ isBanned: true });
          return;
        }

        if (!data.is_supper && (!data.permissions || !data.permissions.length)) {
          return this.setState({
            isLoginChecking: false,
            isPermissionDenied: true,
          });
        }

        localStorage.setItem('token', data['access_token']);
        localStorage.setItem('nickname', data['nickname']);
        localStorage.setItem('is_supper', data['is_supper']);
        localStorage.setItem('permissions', JSON.stringify(data['permissions']));
        localStorage.setItem('host_perms', JSON.stringify(data['host_perms']));
        updatePermissions();

        if (history.location.state && history.location.state['from']) {
          history.push(history.location.state['from'])
        } else {
          if (window.location.pathname === '/') {
            history.push('/welcome/index')
            // window.location.href = '/welcome/index';
          }
        }

        this.setState({ isLoginChecking: false });
      } catch (error) {
        console.log('error', error);
        // const redirectUrl = '/login';
        // history.push('/login');

        localStorage.setItem('token', '');

        this.setState({ isLoginChecking: false });
      }
    }, 1000);
  }

  render() {
    // console.log('isLoginChecking', this.state.isLoginChecking);
    if (this.state.isLoginChecking) {
      return (
        <div
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
        >
          <Spin size="large" />
        </div>
      );
    }

    if (this.state.isBanned) {
      return (
        <Result
          style={{ marginTop: '15%' }}
          status="403"
          title="403"
          subTitle="您的账号已被禁用，请联系管理员"
        />
      );
    }

    if (this.state.isPermissionDenied) {
      return (
        <Result
          style={{ marginTop: '15%' }}
          status="403"
          title="403"
          subTitle="您尚无权限，请联系管理员开通"
        />
      );
    }

    return (
      <Switch>
        <Route path="/" exact component={Login} />
        <Route path="/ssh" exact component={WebSSH} />
        <Route component={Layout} />
      </Switch>
    );
  }
}

export default App;
