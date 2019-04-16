import {AxiosMockType} from 'jest-mock-axios/dist/lib/mock-axios-types'
import MockAxios from 'jest-mock-axios'

type HttpVerbs = 'get' | 'post' | 'put' | 'patch' | 'delete'

type requestHandler = (
  config: { method: HttpVerbs, url: string, data: any, [key: string]: any },
) => any

declare type AxiosRequestMockType = AxiosMockType & { request: requestHandler }

export const MockAxiosRequest: AxiosRequestMockType = {
  ...MockAxios as any,
  request: (
    config: { method: HttpVerbs, url: string, data: any, [key: string]: any }
  ): any => {
    const args = {...config}
    delete args.method
    delete args.url
    delete args.data
    return MockAxios[config.method](config.url, config.data, args)
  },
}

export default MockAxiosRequest
