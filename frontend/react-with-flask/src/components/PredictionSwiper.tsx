import { useEffect, useState } from "react";
import {PredictionCardProps, PredictionCard} from "./PredictionCard";
import { useAuth0 } from '@auth0/auth0-react';

const PredictionSwiper = () =>
{
    const { getAccessTokenSilently } = useAuth0();
    const [matches, setMatches] = useState<PredictionCardProps[]>([])

    useEffect(() => {
        const getPredictions = async () => {
            try
            {
                const token = await getAccessTokenSilently();
                const res = await fetch("api/getPredictions", {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                })

                if (!res.ok) {
                    return
                }
                const data: PredictionCardProps[] = await res.json()
                setMatches(data)
            } catch (e) {
                console.log(e)
            }
        }
        getPredictions()
    }, [])
    
    return (
        <div>
            {matches.map((v,i) => <PredictionCard key={i} {...v}/>)}
        </div>
    )
}

export default PredictionSwiper;